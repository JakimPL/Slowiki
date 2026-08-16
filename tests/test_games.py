import random

import pytest

from wordcore.board.board import Board
from wordcore.exceptions import IllegalMove, InvalidWord
from wordcore.lexicon.lexicon import Lexicon, TextLexicon
from wordcore.moves.action import Exchange, Move, Pass, Play, PlayPlacement
from wordcore.positions.position import Position
from wordcore.states.state import Phase, WordState
from wordcore.tiles.tile import LetterSpec, Tile, TilePreset
from wordgames.backend.base import GameParameters, WordGameRules
from wordtable.build import build_rules
from wordtable.catalogue import resolve_scheme
from wordtable.paths import CONFIG_DIR

TINY_TILES = TilePreset(
    name="tiny",
    letters=(
        LetterSpec(symbol="a", value=1, category="yellow", count=4),
        LetterSpec(symbol="b", value=2, category="green", count=2),
    ),
    blanks=0,
    rack_size=2,
)


def make_tile(identifier: int, letter: str, value: int, category: str, blank: bool = False) -> Tile:
    return Tile(identifier=identifier, letter=letter, value=value, category=category, blank=blank)


def make_board() -> Board:
    return Board(size=3, bonuses=(None,) * 9, tiles=(None,) * 9)


def make_rules(lexicon: Lexicon, players: tuple[int, ...] = (0, 1)) -> WordGameRules:
    parameters = GameParameters(
        validate_on_play=True,
        exchange_limit=None,
        pass_allowed=True,
        pass_end_limit=2,
        scoreless_end_limit=None,
        bingo_bonus=50,
    )
    return WordGameRules(players, make_board(), TINY_TILES, lexicon, parameters)


def make_position(racks: dict[int, tuple[Tile, ...]], bag: tuple[Tile, ...], to_act: int = 0) -> Position:
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


def test_two_passes_end_game() -> None:
    rules = make_rules(TextLexicon.from_words(["ab"]))
    position = make_position(
        racks={
            0: (make_tile(1, "a", 1, "yellow"),),
            1: (make_tile(2, "b", 2, "green"),),
        },
        bag=(),
    )
    first = rules.apply(position, Move(player=0, action=Pass()), random.Random(0))
    assert first.state.phase == Phase.TURN
    second = rules.apply(first, Move(player=1, action=Pass()), random.Random(0))
    assert second.state.phase == Phase.GAME_OVER
    assert second.state.scores == {0: -1, 1: -2}


def test_solo_unlimited_deals_all_tiles() -> None:
    solo_tiles = TINY_TILES.model_copy(update={"rack_size": None})
    parameters = GameParameters(
        validate_on_play=True,
        exchange_limit=None,
        pass_allowed=True,
        pass_end_limit=None,
        scoreless_end_limit=None,
        bingo_bonus=50,
    )
    rules = WordGameRules((0,), make_board(), solo_tiles, TextLexicon.from_words(["ab"]), parameters)
    position = rules.initial_position(random.Random(0))
    assert len(position.state.racks[0]) == 6
    assert position.state.bag == ()


def test_literaki_scheme_builds_and_deals() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    rules = build_rules(resolved, (0, 1), TextLexicon.from_words(["aa"]))
    position = rules.initial_position(random.Random(0))
    assert [len(rack or ()) for rack in position.state.racks.values()] == [7, 7]
    assert len(position.state.bag) == 86
