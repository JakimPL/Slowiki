import random
from typing import Final

import pytest

from wordcore.board.board import Board
from wordcore.errors.exceptions import IllegalMove, InvalidWord
from wordcore.games.game import Game
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.lexicon.protocol import Lexicon
from wordcore.moves.action import Exchange, Pass, Play, PlayPlacement
from wordcore.moves.move import Move
from wordcore.positions.position import Position
from wordcore.states.state import Phase, WordState
from wordcore.tiles.tile import LetterSpec, Tile
from wordcore.tiles.tileset import TileSet
from wordcore.views.projection import project
from wordgames.backend.base import WordGameRules
from wordgames.backend.parameters import GameParameters
from wordtable.build import build_rules
from wordtable.catalog import resolve_scheme
from wordtable.paths import CONFIG_DIR

TINY_TILES = TileSet(
    letters=(
        LetterSpec(symbol="a", value=1, category="yellow", count=4),
        LetterSpec(symbol="b", value=2, category="green", count=2),
    ),
    blanks=0,
)


def make_tile(identifier: int, letter: str, value: int, category: str, blank: bool = False) -> Tile:
    return Tile(identifier=identifier, letter=letter, value=value, category=category, blank=blank)


def make_board() -> Board:
    return Board(size=3, bonuses=(None,) * 9, tiles=(None,) * 9)


TINY_PARAMETERS: Final = GameParameters(
    rack_size=2,
    validate_on_play=True,
    exchange_limit=None,
    exchange_min_bag=7,
    pass_allowed=True,
    opening_tiles=2,
    opening_covers_center=True,
    pass_end_rounds=2,
    scoreless_end_limit=None,
    bingo_bonus=50,
    bingo_tiles=None,
    rack_penalties=True,
    going_out_award=True,
    going_out_bonus=0,
)


def make_rules(lexicon: Lexicon, players: tuple[int, ...] = (0, 1)) -> WordGameRules:
    return WordGameRules(players, make_board(), TINY_TILES, lexicon, TINY_PARAMETERS)


def make_position(
    racks: dict[int, tuple[Tile, ...]],
    bag: tuple[Tile, ...],
    to_act: int = 0,
) -> Position:
    state = WordState(
        phase=Phase.TURN,
        to_act=frozenset({to_act}),
        racks=racks,
        bag=bag,
        scores={seat: 0 for seat in (0, 1)},
        exchange_counts={seat: 0 for seat in (0, 1)},
        consecutive_passes=0,
        premoves={},
        turn_number=0,
    )
    return Position(board=make_board(), state=state, players=(0, 1))


def test_initial_position_deals_racks() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = rules.initial_position(random.Random(0))
    assert position.state.to_act == frozenset({0})
    assert [len(rack or ()) for rack in position.state.racks.values()] == [2, 2]
    assert len(position.state.bag) == 2


def test_play_scores_and_advances() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"), make_tile(2, "b", 2, "green")),
            1: (make_tile(3, "a", 1, "yellow"), make_tile(4, "b", 2, "green")),
        },
        bag=(make_tile(5, "a", 1, "yellow"), make_tile(6, "b", 2, "green")),
    )
    move = Move(
        player=0,
        action=Play(
            placements=(
                PlayPlacement(tile_id=1, row=1, column=0),
                PlayPlacement(tile_id=2, row=1, column=1),
            )
        ),
    )
    rules.validate(position, move)
    updated = rules.apply(position, move, random.Random(0))
    assert updated.state.scores[0] == 53
    assert updated.state.to_act == frozenset({1})
    assert updated.board.tile_at(1, 0) is not None


def test_play_writes_the_last_play_record() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"), make_tile(2, "b", 2, "green")),
            1: (make_tile(3, "a", 1, "yellow"), make_tile(4, "b", 2, "green")),
        },
        bag=(make_tile(5, "a", 1, "yellow"), make_tile(6, "b", 2, "green")),
    )
    move = Move(
        player=0,
        action=Play(
            placements=(
                PlayPlacement(tile_id=1, row=1, column=0),
                PlayPlacement(tile_id=2, row=1, column=1),
            )
        ),
    )
    updated = rules.apply(position, move, random.Random(0))
    record = updated.state.last_play
    assert record is not None
    assert record.player == 0
    assert record.indices == (3, 4)
    assert [(word.text, word.points) for word in record.words] == [("AB", 3)]
    assert record.points == 53
    assert record.bingo == 50
    assert record.turn_number == 0


def test_last_play_survives_passes_and_exchanges() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"), make_tile(2, "b", 2, "green")),
            1: (make_tile(3, "a", 1, "yellow"), make_tile(4, "b", 2, "green")),
        },
        bag=tuple(make_tile(10 + extra, "a", 1, "yellow") for extra in range(9)),
    )
    move = Move(
        player=0,
        action=Play(
            placements=(
                PlayPlacement(tile_id=1, row=1, column=0),
                PlayPlacement(tile_id=2, row=1, column=1),
            )
        ),
    )
    played = rules.apply(position, move, random.Random(0))
    record = played.state.last_play
    passed = rules.apply(played, Move(player=1, action=Pass()), random.Random(0))
    assert passed.state.last_play == record
    exchanged = rules.apply(
        passed,
        Move(player=0, action=Exchange(tile_ids=[10, 11])),
        random.Random(0),
    )
    assert exchanged.state.last_play == record


def test_projection_serves_the_last_play_publicly() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"), make_tile(2, "b", 2, "green")),
            1: (make_tile(3, "a", 1, "yellow"), make_tile(4, "b", 2, "green")),
        },
        bag=(),
    )
    move = Move(
        player=0,
        action=Play(
            placements=(
                PlayPlacement(tile_id=1, row=1, column=0),
                PlayPlacement(tile_id=2, row=1, column=1),
            )
        ),
    )
    updated = rules.apply(position, move, random.Random(0))
    spectator = project(updated, None)
    assert spectator.last_play == updated.state.last_play
    assert spectator.last_play is not None
    assert spectator.scoreless_turns == 0
    assert spectator.racks[0] is None


def test_invalid_word_rejected() -> None:
    rules = make_rules(TextLexicon.from_words(["zz"]))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"), make_tile(2, "b", 2, "green")),
            1: (make_tile(3, "a", 1, "yellow"), make_tile(4, "b", 2, "green")),
        },
        bag=(make_tile(5, "a", 1, "yellow"), make_tile(6, "b", 2, "green")),
    )
    move = Move(
        player=0,
        action=Play(
            placements=(
                PlayPlacement(tile_id=1, row=1, column=0),
                PlayPlacement(tile_id=2, row=1, column=1),
            )
        ),
    )
    with pytest.raises(InvalidWord):
        rules.validate(position, move)


def test_blank_requires_assigned_letter() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = make_position(
        racks={
            0: (make_tile(1, "", 0, "blank", blank=True), make_tile(2, "b", 2, "green")),
            1: (make_tile(3, "a", 1, "yellow"), make_tile(4, "b", 2, "green")),
        },
        bag=(),
    )
    move = Move(
        player=0,
        action=Play(placements=(PlayPlacement(tile_id=1, row=1, column=0),)),
    )
    with pytest.raises(IllegalMove):
        rules.validate(position, move)


def test_exchange_replaces_tiles_and_advances() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    bag = tuple(make_tile(identifier, "a", 1, "yellow") for identifier in range(5, 13))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"), make_tile(2, "b", 2, "green")),
            1: (make_tile(3, "a", 1, "yellow"), make_tile(4, "b", 2, "green")),
        },
        bag=bag,
    )
    move = Move(player=0, action=Exchange(tile_ids=(1,)))
    rules.validate(position, move)
    updated = rules.apply(position, move, random.Random(0))
    assert {tile.identifier for tile in updated.state.racks[0]} == {2, 5}
    assert updated.state.to_act == frozenset({1})


def test_a_round_of_passes_leaves_the_game_running() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"),),
            1: (make_tile(2, "b", 2, "green"),),
        },
        bag=(),
    )
    for seat in (0, 1, 0):
        position = rules.apply(position, Move(player=seat, action=Pass()), random.Random(0))
        assert position.state.phase == Phase.TURN


def test_two_rounds_of_passes_end_game() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"),),
            1: (make_tile(2, "b", 2, "green"),),
        },
        bag=(),
    )
    for seat in (0, 1, 0, 1):
        position = rules.apply(position, Move(player=seat, action=Pass()), random.Random(0))

    assert position.state.phase == Phase.GAME_OVER
    assert position.state.scores == {0: -1, 1: -2}


def test_a_table_without_rack_penalties_keeps_the_scores_it_earned() -> None:
    rules = _ruled({"rack_penalties": False})
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"),),
            1: (make_tile(2, "b", 2, "green"),),
        },
        bag=(),
    )
    for seat in (0, 1, 0, 1):
        position = rules.apply(position, Move(player=seat, action=Pass()), random.Random(0))

    assert position.state.phase == Phase.GAME_OVER
    assert position.state.scores == {0: 0, 1: 0}


def test_a_flat_bonus_rewards_the_finisher_whatever_the_award_does() -> None:
    barred = _went_out(_ruled({"bingo_bonus": 0, "going_out_award": False, "going_out_bonus": 20}))
    assert barred.state.phase == Phase.GAME_OVER
    assert barred.state.scores == {0: 23, 1: -1}
    stacked = _went_out(_ruled({"bingo_bonus": 0, "going_out_bonus": 20}))
    assert stacked.state.scores == {0: 24, 1: -1}


def _ruled(changes: dict[str, object]) -> WordGameRules:
    return WordGameRules(
        (0, 1),
        make_board(),
        TINY_TILES,
        TextLexicon.from_words(["ab"]),
        TINY_PARAMETERS.model_copy(update=changes),
    )


def _went_out(rules: WordGameRules) -> Position:
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"), make_tile(2, "b", 2, "green")),
            1: (make_tile(3, "a", 1, "yellow"),),
        },
        bag=(),
    )
    opening = Move(
        player=0,
        action=Play(
            placements=(
                PlayPlacement(tile_id=1, row=1, column=0),
                PlayPlacement(tile_id=2, row=1, column=1),
            )
        ),
    )
    return rules.apply(position, opening, random.Random(0))


def test_pass_rounds_scale_with_the_seat_count() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]), players=(0, 1, 2))
    state = WordState(
        phase=Phase.TURN,
        to_act=frozenset({0}),
        racks={seat: () for seat in (0, 1, 2)},
        bag=(),
        scores={seat: 0 for seat in (0, 1, 2)},
        exchange_counts={seat: 0 for seat in (0, 1, 2)},
        consecutive_passes=0,
        premoves={},
        turn_number=0,
    )
    position = Position(board=make_board(), state=state, players=(0, 1, 2))
    for seat in (0, 1, 2, 0, 1):
        position = rules.apply(position, Move(player=seat, action=Pass()), random.Random(0))
        assert position.state.phase == Phase.TURN

    position = rules.apply(position, Move(player=2, action=Pass()), random.Random(0))
    assert position.state.phase == Phase.GAME_OVER


def test_solo_unlimited_deals_all_tiles() -> None:
    parameters = TINY_PARAMETERS.model_copy(update={"rack_size": None, "pass_end_rounds": None})
    rules = WordGameRules(
        (0,), make_board(), TINY_TILES, TextLexicon.from_words(["ab"]), parameters
    )
    position = rules.initial_position(random.Random(0))
    assert len(position.state.racks[0]) == 6
    assert position.state.bag == ()


def test_literaki_scheme_builds_and_deals() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    rules = build_rules(resolved, (0, 1), TextLexicon.from_words(["aa"]))
    position = rules.initial_position(random.Random(0))
    assert [len(rack or ()) for rack in position.state.racks.values()] == [7, 7]
    assert len(position.state.bag) == 86


def test_pass_leaves_the_exchange_budget_alone() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"),),
            1: (make_tile(2, "b", 2, "green"),),
        },
        bag=(),
    )
    passed = rules.apply(position, Move(player=0, action=Pass()), random.Random(0))
    assert passed.state.exchange_counts == position.state.exchange_counts
    assert passed.state.consecutive_passes == 1
    assert passed.state.scoreless_turns == 1


def test_game_highlights_walk_the_journal() -> None:
    rules = make_rules(TextLexicon.from_words(["ab", "aa"]))
    game = Game(rules, random.Random(0), premoves_allowed=True)
    game.submit(
        Move(
            player=0,
            action=Play(
                placements=(
                    PlayPlacement(tile_id=2, row=1, column=0),
                    PlayPlacement(tile_id=4, row=1, column=1),
                )
            ),
        ),
        base_seq=0,
    )
    game.submit(
        Move(player=1, action=Play(placements=(PlayPlacement(tile_id=1, row=0, column=0),))),
        base_seq=1,
    )
    highlights = game.highlights()
    assert highlights.best_word is not None
    assert highlights.best_word.player == 0
    assert highlights.best_word.word == "AB"
    assert highlights.best_word == highlights.longest_word


def test_a_game_yet_to_be_played_has_no_highlights() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    game = Game(rules, random.Random(0), premoves_allowed=True)
    assert game.highlights().best_word is None
    assert game.highlights().longest_word is None


def test_a_bingo_fires_at_the_tile_count_the_rules_state() -> None:
    rules = WordGameRules(
        (0, 1),
        make_board(),
        TINY_TILES,
        TextLexicon.from_words(["ab"]),
        TINY_PARAMETERS.model_copy(update={"rack_size": 3, "bingo_tiles": 2}),
    )
    position = make_position(
        racks={
            0: (
                make_tile(1, "a", 1, "yellow"),
                make_tile(2, "b", 2, "green"),
                make_tile(5, "a", 1, "yellow"),
            ),
            1: (make_tile(3, "a", 1, "yellow"), make_tile(4, "b", 2, "green")),
        },
        bag=(make_tile(6, "b", 2, "green"),),
    )
    move = Move(
        player=0,
        action=Play(
            placements=(
                PlayPlacement(tile_id=1, row=1, column=0),
                PlayPlacement(tile_id=2, row=1, column=1),
            )
        ),
    )
    record = rules.apply(position, move, random.Random(0)).state.last_play
    assert record is not None
    assert record.bingo == 50


def test_a_bingo_stays_quiet_below_the_tile_count() -> None:
    rules = WordGameRules(
        (0, 1),
        make_board(),
        TINY_TILES,
        TextLexicon.from_words(["ab"]),
        TINY_PARAMETERS.model_copy(update={"rack_size": 3, "bingo_tiles": 3}),
    )
    position = make_position(
        racks={
            0: (
                make_tile(1, "a", 1, "yellow"),
                make_tile(2, "b", 2, "green"),
                make_tile(5, "a", 1, "yellow"),
            ),
            1: (make_tile(3, "a", 1, "yellow"), make_tile(4, "b", 2, "green")),
        },
        bag=(make_tile(6, "b", 2, "green"),),
    )
    move = Move(
        player=0,
        action=Play(
            placements=(
                PlayPlacement(tile_id=1, row=1, column=0),
                PlayPlacement(tile_id=2, row=1, column=1),
            )
        ),
    )
    record = rules.apply(position, move, random.Random(0)).state.last_play
    assert record is not None
    assert record.bingo == 0
