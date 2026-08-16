import random

import pytest

from wordcore.board.board import Bonus, BonusKind, Board
from wordcore.tiles.tile import LetterSpec, Tile, TilePreset
from wordcore.tiles.bag import build_tiles, deal_racks, shuffled_bag
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.moves.action import Move, Pass, Play, PlayPlacement
from wordcore.games.game import Game
from wordcore.exceptions import IllegalMove, NotYourTurn, StalePosition
from tests.games.trivial import TrivialRules


def make_board() -> Board:
    bonuses = (None,) * 9
    tiles = (None,) * 9
    return Board(size=3, bonuses=bonuses, tiles=tiles)


def test_board_indexing() -> None:
    board = make_board()
    assert board.index(1, 2) == 5
    assert board.in_bounds(0, 0)
    assert board.in_bounds(2, 2)
    assert not board.in_bounds(3, 0)
    assert board.center() == 1
    assert board.is_empty()


def test_board_with_tiles() -> None:
    board = make_board()
    tile = Tile(identifier=1, letter="a", value=1, category="yellow", blank=False)
    updated = board.with_tiles({4: tile})
    assert updated.tile_at(1, 1) == tile
    assert board.tile_at(1, 1) is None


def test_bonus_kinds() -> None:
    board = Board(
        size=1,
        bonuses=(Bonus(kind=BonusKind.WORD_MULTIPLIER, multiplier=3),),
        tiles=(None,),
    )
    bonus = board.bonus_at(0, 0)
    assert bonus is not None
    assert bonus.kind == BonusKind.WORD_MULTIPLIER
    assert bonus.multiplier == 3


def test_bag_counts() -> None:
    preset = TilePreset(
        name="tiny",
        letters=(LetterSpec(symbol="a", value=1, category="yellow", count=3),),
        blanks=1,
        rack_size=2,
    )
    tiles = build_tiles(preset)
    assert len(tiles) == 4
    assert sum(1 for tile in tiles if tile.blank) == 1


def test_shuffled_bag_is_deterministic() -> None:
    preset = TilePreset(
        name="tiny",
        letters=(LetterSpec(symbol="a", value=1, category="yellow", count=5),),
        blanks=0,
        rack_size=2,
    )
    first = shuffled_bag(preset, random.Random(7))
    second = shuffled_bag(preset, random.Random(7))
    assert first == second


def test_deal_racks() -> None:
    preset = TilePreset(
        name="tiny",
        letters=(LetterSpec(symbol="a", value=1, category="yellow", count=4),),
        blanks=0,
        rack_size=2,
    )
    bag = shuffled_bag(preset, random.Random(1))
    racks, remaining = deal_racks(bag, {0: 2, 1: None})
    assert len(racks[0]) == 2
    assert len(racks[1]) == 2
    assert remaining == ()


def test_text_lexicon() -> None:
    lexicon = TextLexicon.from_words(["kot", "kota", "dom", "i"])
    assert lexicon.judge("kot").allowed
    assert lexicon.judge("KOT").allowed
    assert not lexicon.judge("koty").allowed
    assert lexicon.has_prefix("ko")
    assert not lexicon.has_prefix("dome")


def test_engine_submit_and_turn() -> None:
    game = Game(TrivialRules(), random.Random(0))
    assert game.seq == 0
    game.submit(Move(player=0, action=Pass()), base_seq=0)
    assert game.seq == 1
    assert game.position.state.to_act == frozenset({1})


def test_engine_not_your_turn() -> None:
    game = Game(TrivialRules(), random.Random(0))
    with pytest.raises(NotYourTurn):
        game.submit(Move(player=1, action=Pass()), base_seq=0)


def test_engine_stale_position() -> None:
    game = Game(TrivialRules(), random.Random(0))
    with pytest.raises(StalePosition):
        game.submit(Move(player=0, action=Pass()), base_seq=1)


def test_engine_illegal_move() -> None:
    game = Game(TrivialRules(), random.Random(0))
    with pytest.raises(IllegalMove):
        game.submit(
            Move(
                player=0,
                action=Play(placements=(PlayPlacement(tile_id=1, row=0, column=0),)),
            ),
            base_seq=0,
        )


def test_engine_premove_executes() -> None:
    game = Game(TrivialRules(), random.Random(0))
    game.submit(Move(player=1, action=Pass()), base_seq=0, premove=True)
    assert game.position.state.premoves == {1: Move(player=1, action=Pass())}
    game.submit(Move(player=0, action=Pass()), base_seq=1)
    assert game.position.state.premoves == {1: None}
    assert game.position.state.to_act == frozenset({0})
    assert game.position.state.turn_number == 2


def test_engine_premove_discarded_when_invalid() -> None:
    rules = TrivialRules()
    game = Game(rules, random.Random(0))
    game.submit(Move(player=1, action=Pass()), base_seq=0, premove=True)
    rules.reject_seat = 1
    game.submit(Move(player=0, action=Pass()), base_seq=1)
    assert game.position.state.premoves == {1: None}
    assert game.position.state.to_act == frozenset({1})
    assert game.position.state.turn_number == 1


def test_engine_projection_hides_other_racks() -> None:
    rules = TrivialRules()
    game = Game(rules, random.Random(0))
    view = game.view(observer=0)
    assert view.racks[0] is not None
    assert view.racks[1] is None
    spectator = game.view(observer=None)
    assert spectator.racks[0] is None
    assert spectator.racks[1] is None
