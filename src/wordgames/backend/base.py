import random

from wordcore.board.board import Board
from wordcore.errors.exceptions import IllegalMove
from wordcore.games.rules import Rules
from wordcore.lexicon.protocol import Lexicon
from wordcore.moves.action import Exchange, Pass, Play, PlayPlacement
from wordcore.moves.move import Move
from wordcore.positions.position import Position
from wordcore.rules.end_conditions import final_scores
from wordcore.rules.exchange import apply_exchange, validate_exchange
from wordcore.rules.rack import rack_of
from wordcore.rules.score.move import MoveScore
from wordcore.rules.score.scoring import score_move
from wordcore.rules.turn import next_seat
from wordcore.rules.validity import validate_words
from wordcore.rules.words.formed import formed_words, validate_anchor
from wordcore.rules.words.placement import Placement, board_with_placements
from wordcore.states.phase import Phase
from wordcore.states.record import PlayRecord
from wordcore.states.state import WordState
from wordcore.tiles.bag import deal_racks, shuffled_bag
from wordcore.tiles.tile import Tile
from wordcore.tiles.tileset import TileSet
from wordgames.backend.parameters import GameParameters


class WordGameRules(Rules):
    def __init__(
        self,
        players: tuple[int, ...],
        board: Board,
        tiles: TileSet,
        lexicon: Lexicon,
        parameters: GameParameters,
    ) -> None:
        self._players = players
        self._board = board
        self._tiles = tiles
        self._lexicon = lexicon
        self._parameters = parameters

    def initial_position(self, rng: random.Random) -> Position:
        bag = shuffled_bag(self._tiles, rng)
        racks, remaining = deal_racks(
            bag,
            {seat: self._parameters.rack_size for seat in self._players},
        )
        state = WordState(
            phase=Phase.TURN,
            to_act=frozenset({self._players[0]}),
            racks=racks,
            bag=remaining,
            scores={seat: 0 for seat in self._players},
            exchange_counts={seat: 0 for seat in self._players},
            consecutive_passes=0,
            premoves={},
            turn_number=0,
        )
        return Position(
            board=self._board,
            state=state,
            players=self._players,
        )

    def validate(self, position: Position, move: Move) -> None:
        action = move.action
        match action:
            case Play():
                self._validate_play(position, move.player, action)
            case Exchange():
                self._validate_exchange(position, move.player, action)
            case Pass():
                self._validate_pass()

    def apply(
        self,
        position: Position,
        move: Move,
        _rng: random.Random,
    ) -> Position:
        action = move.action
        match action:
            case Play():
                played, went_out = self._apply_play(
                    position,
                    move.player,
                    action,
                )
                return self._finish_turn(
                    played,
                    move.player,
                    went_out=went_out,
                )
            case Exchange():
                return self._finish_turn(
                    self._apply_exchange(position, move.player, action),
                    move.player,
                    went_out=None,
                )
            case Pass():
                return self._finish_turn(
                    self._apply_pass(position),
                    move.player,
                    went_out=None,
                )

    def _validate_play(
        self,
        position: Position,
        player: int,
        action: Play,
    ) -> None:
        placements = self._resolve_placements(position, player, action)
        validate_anchor(
            position.board,
            placements,
            opening_tiles=self._parameters.opening_tiles,
            opening_covers_center=self._parameters.opening_covers_center,
        )
        words = formed_words(position.board, placements)
        validate_words(
            self._lexicon,
            words,
            self._parameters.validate_on_play,
        )

    def _validate_exchange(
        self,
        position: Position,
        player: int,
        action: Exchange,
    ) -> None:
        validate_exchange(
            position,
            player,
            action,
            limit=self._parameters.exchange_limit,
            min_bag=self._parameters.exchange_min_bag,
        )

    def _validate_pass(self) -> None:
        if not self._parameters.pass_allowed:
            raise IllegalMove("passing is not allowed")

    def _apply_play(
        self,
        position: Position,
        player: int,
        action: Play,
    ) -> tuple[Position, int | None]:
        placements = self._resolve_placements(position, player, action)
        words = formed_words(position.board, placements)
        scored = score_move(
            position.board,
            words,
            self._bingo_bonus(len(placements)),
        )
        record = self._play_record(position, player, placements, scored)
        new_rack, new_bag = self._replenished_rack(
            position,
            player,
            placements,
        )
        new_state = self._state_after_play(
            position.state,
            player,
            scored,
            record,
            new_rack,
            new_bag,
        )
        played = position.model_copy(
            update={
                "board": board_with_placements(position.board, placements),
                "state": new_state,
            }
        )
        return played, self._went_out(player, new_rack, new_bag)

    def _replenished_rack(
        self,
        position: Position,
        player: int,
        placements: tuple[Placement, ...],
    ) -> tuple[tuple[Tile, ...], tuple[Tile, ...]]:
        played = {placement.tile.identifier for placement in placements}
        kept = tuple(tile for tile in rack_of(position, player) if tile.identifier not in played)
        rack_size = self._parameters.rack_size
        if rack_size is None:
            return kept, position.state.bag

        needed = max(0, rack_size - len(kept))
        return kept + position.state.bag[:needed], position.state.bag[needed:]

    def _apply_exchange(self, position: Position, player: int, action: Exchange) -> Position:
        updated = apply_exchange(position, player, action)
        new_state = updated.state.model_copy(
            update={
                "consecutive_passes": 0,
                "scoreless_turns": updated.state.scoreless_turns + 1,
            }
        )
        return updated.model_copy(update={"state": new_state})

    def _apply_pass(self, position: Position) -> Position:
        state = position.state
        new_state = state.model_copy(
            update={
                "consecutive_passes": state.consecutive_passes + 1,
                "scoreless_turns": state.scoreless_turns + 1,
            }
        )
        return position.model_copy(update={"state": new_state})

    def _finish_turn(
        self,
        position: Position,
        mover: int,
        *,
        went_out: int | None,
    ) -> Position:
        if went_out is not None:
            return self._finish_game(position, went_out=went_out)

        if self._end_limit_reached(position.state):
            return self._finish_game(position, went_out=None)

        if self._solo_ended(position, mover):
            return self._finish_game(position, went_out=None)

        return self._advance_turn(position, mover)

    def _end_limit_reached(self, state: WordState) -> bool:
        return self._passes_exhausted(state) or self._scoreless_exhausted(state)

    def _passes_exhausted(self, state: WordState) -> bool:
        rounds = self._parameters.pass_end_rounds
        if rounds is None:
            return False

        return state.consecutive_passes >= rounds * len(self._players)

    def _scoreless_exhausted(self, state: WordState) -> bool:
        limit = self._parameters.scoreless_end_limit
        if limit is None:
            return False

        return state.scoreless_turns >= limit

    def _solo_ended(self, position: Position, mover: int) -> bool:
        if len(self._players) != 1:
            return False

        return not rack_of(position, mover) or position.state.consecutive_passes >= 1

    def _advance_turn(self, position: Position, mover: int) -> Position:
        next_player = next_seat(self._players, mover)
        new_state = position.state.model_copy(
            update={
                "to_act": frozenset({next_player}),
                "turn_number": position.state.turn_number + 1,
            }
        )
        return position.model_copy(update={"state": new_state})

    def _finish_game(
        self,
        position: Position,
        *,
        went_out: int | None,
    ) -> Position:
        new_state = position.state.model_copy(
            update={
                "phase": Phase.GAME_OVER,
                "scores": final_scores(
                    position,
                    went_out,
                    going_out_award=self._parameters.going_out_award,
                ),
                "to_act": frozenset(),
            }
        )
        return position.model_copy(update={"state": new_state})

    def _resolve_placements(
        self,
        position: Position,
        player: int,
        action: Play,
    ) -> tuple[Placement, ...]:
        by_id = {tile.identifier: tile for tile in rack_of(position, player)}
        result: list[Placement] = []
        seen: set[int] = set()
        for spec in action.placements:
            if spec.tile_id in seen:
                raise IllegalMove("a tile is placed more than once")

            seen.add(spec.tile_id)
            result.append(
                Placement(
                    tile=self._resolved_tile(by_id, spec),
                    row=spec.row,
                    column=spec.column,
                )
            )

        return tuple(result)

    def _bingo_bonus(self, played: int) -> int:
        threshold = self._bingo_threshold()
        if threshold is not None and played >= threshold:
            return self._parameters.bingo_bonus

        return 0

    def _bingo_threshold(self) -> int | None:
        if self._parameters.bingo_tiles is not None:
            return self._parameters.bingo_tiles

        return self._parameters.rack_size

    @staticmethod
    def _resolved_tile(
        rack_by_id: dict[int, Tile],
        spec: PlayPlacement,
    ) -> Tile:
        tile = rack_by_id.get(spec.tile_id)
        if tile is None:
            raise IllegalMove("placed tile is not in the rack")

        if tile.blank:
            return WordGameRules._assigned_blank(tile, spec.letter)

        return tile

    @staticmethod
    def _assigned_blank(tile: Tile, letter: str | None) -> Tile:
        if letter is None or len(letter) != 1 or not letter.isalpha():
            raise IllegalMove("a blank tile requires a single assigned letter")

        return tile.model_copy(update={"letter": letter})

    @staticmethod
    def _play_record(
        position: Position,
        player: int,
        placements: tuple[Placement, ...],
        scored: MoveScore,
    ) -> PlayRecord:
        indices = tuple(
            sorted(
                position.board.index(
                    placement.row,
                    placement.column,
                )
                for placement in placements
            )
        )
        return PlayRecord(
            player=player,
            indices=indices,
            words=scored.words,
            points=scored.points,
            bingo=scored.bingo,
            turn_number=position.state.turn_number,
        )

    @staticmethod
    def _state_after_play(
        state: WordState,
        player: int,
        scored: MoveScore,
        record: PlayRecord,
        new_rack: tuple[Tile, ...],
        new_bag: tuple[Tile, ...],
    ) -> WordState:
        return state.model_copy(
            update={
                "racks": {**state.racks, player: new_rack},
                "bag": new_bag,
                "scores": {
                    **state.scores,
                    player: state.scores[player] + scored.points,
                },
                "consecutive_passes": 0,
                "scoreless_turns": 0 if scored.points else state.scoreless_turns + 1,
                "last_play": record,
            }
        )

    @staticmethod
    def _went_out(
        player: int,
        rack: tuple[Tile, ...],
        bag: tuple[Tile, ...],
    ) -> int | None:
        if not rack and not bag:
            return player

        return None
