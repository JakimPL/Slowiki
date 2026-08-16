import random

from wordcore.board.board import Board
from wordcore.exceptions import IllegalMove
from wordcore.games.rules import Rules
from wordcore.lexicon.protocol import Lexicon
from wordcore.moves.action import Exchange, Pass, Play, Reorder
from wordcore.moves.move import Move
from wordcore.positions.position import Position
from wordcore.rules.end_conditions import final_scores
from wordcore.rules.exchange import apply_exchange, validate_exchange
from wordcore.rules.rack import rack_of
from wordcore.rules.score.scoring import score_move
from wordcore.rules.turn import next_seat
from wordcore.rules.validity import validate_words
from wordcore.rules.words.formed import formed_words, validate_anchor
from wordcore.rules.words.placement import Placement
from wordcore.states.state import Phase, WordState
from wordcore.tiles.bag import deal_racks, shuffled_bag
from wordcore.tiles.tile import Tile, TilePreset
from wordgames.backend.parameters import GameParameters


# TODO: does not look like base responsibility
def _board_with_placements(
    board: Board,
    placements: tuple[Placement, ...],
) -> Board:
    return board.with_tiles(
        {
            board.index(
                placement.row,
                placement.column,
            ): placement.tile
            for placement in placements
        }
    )


# TODO: refactor, this class is a mess
# hardcoded constants that supposed to be configurable
# unreasonably convoluted functions
class WordGameRules(Rules):
    def __init__(
        self,
        players: tuple[int, ...],
        board: Board,
        tiles: TilePreset,
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
        racks, remaining = deal_racks(bag, {seat: self._tiles.rack_size for seat in self._players})
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
                placements = self._resolve_placements(
                    position,
                    move.player,
                    action,
                )
                validate_anchor(position.board, placements)
                words = formed_words(position.board, placements)
                validate_words(
                    self._lexicon,
                    words,
                    self._parameters.validate_on_play,
                )

            case Exchange():
                validate_exchange(
                    position,
                    move.player,
                    action,
                    limit=self._parameters.exchange_limit,
                    min_bag=7,  # TODO: this should be configurable
                )

            case Pass():
                if not self._parameters.pass_allowed:
                    raise IllegalMove("passing is not allowed")

            case Reorder():
                self._validate_reorder(position, move.player, action)

    def apply(
        self,
        position: Position,
        move: Move,
        _rng: random.Random,
    ) -> Position:
        action = move.action
        match action:
            case Play():
                intermediate, went_out = self._apply_play(
                    position,
                    move.player,
                    action,
                )
                return self._finish_turn(intermediate, move.player, went_out)
            case Exchange():
                intermediate = self._apply_exchange(
                    position,
                    move.player,
                    action,
                )
                return self._finish_turn(intermediate, move.player, None)
            case Pass():
                intermediate = self._apply_pass(position)
                return self._finish_turn(intermediate, move.player, None)
            case Reorder():
                return self._apply_reorder(position, move.player, action)

    def _apply_play(
        self,
        position: Position,
        player: int,
        action: Play,
    ) -> tuple[Position, int | None]:
        placements = self._resolve_placements(position, player, action)
        board = _board_with_placements(position.board, placements)
        words = formed_words(position.board, placements)
        scored = score_move(
            position.board,
            words,
            self._bingo_bonus(len(placements)),
        )
        new_rack, new_bag = self._replenished_rack(
            position,
            player,
            placements,
        )
        new_state = position.state.model_copy(
            update={
                "racks": {**position.state.racks, player: new_rack},
                "bag": new_bag,
                "scores": {
                    **position.state.scores,
                    player: position.state.scores[player] + scored.points,
                },
                "consecutive_passes": 0,
                "scoreless_turns": 0,
            }
        )
        went_out = player if not new_rack and not new_bag else None
        return (
            position.model_copy(
                update={
                    "board": board,
                    "state": new_state,
                }
            ),
            went_out,
        )

    def _replenished_rack(
        self, position: Position, player: int, placements: tuple[Placement, ...]
    ) -> tuple[tuple[Tile, ...], tuple[Tile, ...]]:
        played = {placement.tile.identifier for placement in placements}
        kept = tuple(
            tile
            for tile in rack_of(
                position,
                player,
            )
            if tile.identifier not in played
        )
        rack_size = self._tiles.rack_size
        if rack_size is None:
            return kept, position.state.bag

        needed = max(0, rack_size - len(kept))
        return kept + position.state.bag[:needed], position.state.bag[needed:]

    def _apply_exchange(
        self,
        position: Position,
        player: int,
        action: Exchange,
    ) -> Position:
        updated = apply_exchange(position, player, action)
        state = updated.state
        new_state = state.model_copy(
            update={
                "consecutive_passes": 0,
                "scoreless_turns": state.scoreless_turns + 1,
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

    def _validate_reorder(
        self,
        position: Position,
        player: int,
        action: Reorder,
    ) -> None:
        rack_ids = [tile.identifier for tile in rack_of(position, player)]
        if sorted(action.tile_ids) != sorted(rack_ids):
            raise IllegalMove("reorder must list every rack tile exactly once")

    def _apply_reorder(
        self,
        position: Position,
        player: int,
        action: Reorder,
    ) -> Position:
        by_id = {tile.identifier: tile for tile in rack_of(position, player)}
        ordered = tuple(by_id[tile_id] for tile_id in action.tile_ids)
        new_state = position.state.model_copy(
            update={
                "racks": {
                    **position.state.racks,
                    player: ordered,
                }
            }
        )
        return position.model_copy(update={"state": new_state})

    def _finish_turn(
        self,
        position: Position,
        mover: int,
        went_out: int | None,
    ) -> Position:
        if went_out is not None:
            return self._finish_game(position, went_out)

        if self._end_limit_reached(position.state):
            return self._finish_game(position, None)

        if self._solo_ended(position, mover):
            return self._finish_game(position, None)

        return self._advance_turn(position, mover)

    def _end_limit_reached(self, state: WordState) -> bool:
        pass_limit = self._parameters.pass_end_limit
        if pass_limit is not None and state.consecutive_passes >= pass_limit:
            return True

        scoreless_limit = self._parameters.scoreless_end_limit
        return scoreless_limit is not None and state.scoreless_turns >= scoreless_limit

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
        went_out: int | None,
    ) -> Position:
        state = position.state
        scores = final_scores(position, went_out)
        new_state = state.model_copy(
            update={
                "phase": Phase.GAME_OVER,
                "scores": scores,
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
            tile = by_id.get(spec.tile_id)
            if tile is None:
                raise IllegalMove("placed tile is not in the rack")

            if tile.blank:
                if spec.letter is None or len(spec.letter) != 1 or not spec.letter.isalpha():
                    raise IllegalMove("a blank tile requires a single assigned letter")

                tile = tile.model_copy(update={"letter": spec.letter})

            result.append(
                Placement(
                    tile=tile,
                    row=spec.row,
                    column=spec.column,
                )
            )

        return tuple(result)

    def _bingo_bonus(self, played: int) -> int:
        rack_size = self._tiles.rack_size
        if rack_size is not None and played == rack_size:
            return self._parameters.bingo_bonus

        return 0
