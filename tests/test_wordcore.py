import random

import pytest
from tests.games.trivial import TrivialRules

from wordcore.board.board import Board
from wordcore.board.bonus import Bonus, BonusKind
from wordcore.errors.exceptions import (
    IllegalMove,
    NoPremove,
    NotYourTurn,
    StalePosition,
)
from wordcore.errors.rejections import RejectionCode
from wordcore.games.game import Game
from wordcore.games.journal import EntryKind, JournalEntry
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.moves.action import Exchange, Pass, Play, PlayPlacement, Reorder
from wordcore.moves.move import Move
from wordcore.tiles.bag import build_tiles, deal_racks, shuffled_bag
from wordcore.tiles.tile import LetterSpec, Tile, TilePreset
from wordcore.views.events import event_view


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


def queued_exchange() -> Move:
    return Move(player=1, action=Exchange(tile_ids=(9,)))


def test_engine_submit_and_turn() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    assert game.seq == 0
    game.submit(Move(player=0, action=Pass()), base_seq=0)
    assert game.seq == 1
    assert game.position.state.to_act == frozenset({1})


def test_engine_not_your_turn() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    with pytest.raises(NotYourTurn):
        game.submit(Move(player=1, action=Pass()), base_seq=0)


def test_engine_stale_position() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    with pytest.raises(StalePosition):
        game.submit(Move(player=0, action=Pass()), base_seq=1)


def test_engine_illegal_move() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    with pytest.raises(IllegalMove):
        game.submit(
            Move(
                player=0,
                action=Play(placements=(PlayPlacement(tile_id=1, row=0, column=0),)),
            ),
            base_seq=0,
        )


def test_engine_premove_waits_for_its_settlement() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    assert game.position.state.premoves == {1: queued_exchange()}
    game.submit(Move(player=0, action=Pass()), base_seq=1)
    assert game.position.state.premoves == {1: queued_exchange()}
    assert game.position.state.to_act == frozenset({1})
    settled = game.settle_premove()
    assert settled is not None
    assert settled.move == queued_exchange()
    assert game.position.state.premoves == {1: None}
    assert game.position.state.to_act == frozenset({0})
    assert game.position.state.turn_number == 2


def test_engine_settles_nothing_without_a_premove() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    assert game.settle_premove() is None
    assert game.seq == 0


def test_engine_premove_discarded_when_invalid() -> None:
    rules = TrivialRules()
    game = Game(rules, random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    rules.reject_seat = 1
    game.submit(Move(player=0, action=Pass()), base_seq=1)
    discarded = game.settle_premove()
    assert discarded is not None
    assert discarded.kind == EntryKind.PREMOVE_DISCARDED
    assert game.position.state.premoves == {1: None}
    assert game.position.state.to_act == frozenset({1})
    assert game.position.state.turn_number == 1


def test_premoves_can_be_disabled() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=False)
    with pytest.raises(IllegalMove):
        game.submit(queued_exchange(), base_seq=0, premove=True)
    assert game.seq == 0


def test_engine_refuses_a_queued_pass() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    with pytest.raises(IllegalMove):
        game.submit(Move(player=1, action=Pass()), base_seq=0, premove=True)
    assert game.seq == 0
    assert game.position.state.premoves == {}


def test_engine_refuses_a_queued_reorder() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    with pytest.raises(IllegalMove):
        game.submit(Move(player=1, action=Reorder(tile_ids=())), base_seq=0, premove=True)
    assert game.seq == 0


def test_cancel_premove_records_a_transaction() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    entry = game.cancel_premove(1, base_seq=1)
    assert game.seq == 2
    assert entry.kind == EntryKind.PREMOVE_CLEARED
    assert entry.move is None
    assert entry.actor == 1
    assert game.position.state.premoves == {1: None}
    cleared = game.events(observer=0, since=1)[0]
    assert cleared.kind == EntryKind.PREMOVE_CLEARED
    assert cleared.actor == 1
    assert cleared.move is None


def test_discard_premove_records_the_reason() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    entry = game.discard_premove(1, base_seq=1, reason=RejectionCode.OUT_OF_TIME)
    assert game.seq == 2
    assert entry.kind == EntryKind.PREMOVE_DISCARDED
    assert entry.move is None
    assert entry.actor == 1
    assert entry.reason == RejectionCode.OUT_OF_TIME
    assert game.position.state.premoves == {1: None}


def test_discard_premove_requires_a_queued_premove() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    with pytest.raises(NoPremove):
        game.discard_premove(1, base_seq=0, reason=RejectionCode.OUT_OF_TIME)


def test_cancel_premove_requires_a_queued_premove() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    with pytest.raises(NoPremove):
        game.cancel_premove(1, base_seq=0)


def test_cancel_premove_requires_current_sequence() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    with pytest.raises(StalePosition):
        game.cancel_premove(1, base_seq=0)


def test_projection_shows_own_premove_and_public_pending() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    owner = game.view(observer=1)
    assert owner.premove == queued_exchange()
    assert owner.pending_premoves == frozenset({1})
    other = game.view(observer=0)
    assert other.premove is None
    assert other.pending_premoves == frozenset({1})
    spectator = game.view(observer=None)
    assert spectator.premove is None
    assert spectator.pending_premoves == frozenset({1})


def test_events_mask_premove_content_per_observer() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    owned = game.events(observer=1, since=0)[0]
    assert owned.kind == EntryKind.PREMOVE_SET
    assert owned.actor == 1
    assert owned.move == queued_exchange()
    other = game.events(observer=0, since=0)[0]
    assert other.kind == EntryKind.PREMOVE_SET
    assert other.actor == 1
    assert other.move is None
    spectator = game.events(observer=None, since=0)[0]
    assert spectator.move is None


def test_discard_reason_reaches_owner_only() -> None:
    rules = TrivialRules()
    game = Game(rules, random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    rules.reject_seat = 1
    game.submit(Move(player=0, action=Pass()), base_seq=1)
    game.settle_premove()
    owned = game.events(observer=1, since=2)[0]
    assert owned.kind == EntryKind.PREMOVE_DISCARDED
    assert owned.actor == 1
    assert owned.move is None
    assert owned.reason == RejectionCode.ILLEGAL_MOVE
    other = game.events(observer=0, since=2)[0]
    assert other.kind == EntryKind.PREMOVE_DISCARDED
    assert other.reason is None


def test_settled_premove_becomes_public_move() -> None:
    game = Game(TrivialRules(), random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    game.submit(Move(player=0, action=Pass()), base_seq=1)
    game.settle_premove()
    settled = game.events(observer=0, since=2)[0]
    assert settled.kind == EntryKind.MOVE
    assert settled.actor == 1
    assert settled.move == queued_exchange()


def test_reorder_content_stays_with_its_owner() -> None:
    rules = TrivialRules()
    position = rules.initial_position(random.Random(0))
    entry = JournalEntry(
        kind=EntryKind.MOVE,
        move=Move(player=0, action=Reorder(tile_ids=(2, 1))),
        actor=0,
        reason=None,
        position=position,
    )
    assert event_view(entry, 0, observer=0).move is not None
    assert event_view(entry, 0, observer=1).move is None
    assert event_view(entry, 0, observer=None).move is None


def test_late_subscriber_reads_the_same_masked_history() -> None:
    rules = TrivialRules()
    game = Game(rules, random.Random(0), premoves_allowed=True)
    game.submit(queued_exchange(), base_seq=0, premove=True)
    game.submit(Move(player=0, action=Pass()), base_seq=1)
    game.settle_premove()
    live = game.events(observer=0, since=0)
    resumed = game.events(observer=0, since=0)[:1] + game.events(observer=0, since=1)
    assert live == resumed
    assert [event.seq for event in live] == [0, 1, 2]


def test_engine_projection_hides_other_racks() -> None:
    rules = TrivialRules()
    game = Game(rules, random.Random(0), premoves_allowed=True)
    view = game.view(observer=0)
    assert view.racks[0] is not None
    assert view.racks[1] is None
    spectator = game.view(observer=None)
    assert spectator.racks[0] is None
    assert spectator.racks[1] is None
