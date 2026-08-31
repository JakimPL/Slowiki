from typing import Final

import pytest

from wordcore.board.board import Board
from wordcore.board.bonus import Bonus, BonusKind
from wordcore.errors.exceptions import IllegalMove, InvalidWord
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.moves.action import Exchange
from wordcore.positions.position import Position
from wordcore.rules.end_conditions import final_scores
from wordcore.rules.exchange import apply_exchange, validate_exchange
from wordcore.rules.score.scoring import score_move
from wordcore.rules.turn import next_seat, next_seat_among
from wordcore.rules.validity import validate_words
from wordcore.rules.words.formed import formed_words, validate_anchor
from wordcore.rules.words.placement import Placement
from wordcore.states.state import Phase, WordState
from wordcore.tiles.tile import Tile

_PENALTIES_APPLY: Final = True
_AWARD_STANDS: Final = True
_NO_FLAT_BONUS: Final = 0


def tile(identifier: int, letter: str, value: int, category: str) -> Tile:
    return Tile(identifier=identifier, letter=letter, value=value, category=category, blank=False)


def make_board(size: int, bonuses: tuple[Bonus | None, ...]) -> Board:
    return Board(size=size, bonuses=bonuses, tiles=(None,) * (size * size))


def empty_position() -> Position:
    return Position(
        board=make_board(3, (None,) * 9),
        state=WordState(
            phase=Phase.TURN,
            to_act=frozenset({0}),
            racks={0: (), 1: ()},
            bag=(),
            scores={0: 0, 1: 0},
            exchange_counts={0: 0, 1: 0},
            consecutive_passes=0,
            premoves={},
            turn_number=0,
        ),
        players=(0, 1),
    )


def test_formed_words_horizontal_with_cross() -> None:
    board = make_board(3, (None,) * 9)
    board = board.with_tiles({board.index(1, 0): tile(1, "a", 1, "yellow")})
    board = board.with_tiles({board.index(0, 2): tile(2, "c", 1, "yellow")})
    placements = (
        Placement(tile=tile(3, "b", 1, "yellow"), row=1, column=1),
        Placement(tile=tile(4, "c", 1, "yellow"), row=1, column=2),
    )
    words = formed_words(board, placements)
    assert {word.text for word in words} == {"ABC", "CC"}


def test_formed_words_single_tile_two_directions() -> None:
    board = make_board(3, (None,) * 9)
    board = board.with_tiles({board.index(1, 0): tile(1, "a", 1, "yellow")})
    board = board.with_tiles({board.index(0, 1): tile(2, "b", 1, "yellow")})
    placements = (Placement(tile=tile(3, "c", 1, "yellow"), row=1, column=1),)
    words = formed_words(board, placements)
    assert {word.text for word in words} == {"AC", "BC"}


def test_formed_words_reject_gap() -> None:
    board = make_board(3, (None,) * 9)
    placements = (
        Placement(tile=tile(1, "a", 1, "yellow"), row=1, column=0),
        Placement(tile=tile(2, "b", 1, "yellow"), row=1, column=2),
    )
    with pytest.raises(IllegalMove):
        formed_words(board, placements)


def test_formed_words_reject_not_collinear() -> None:
    board = make_board(3, (None,) * 9)
    placements = (
        Placement(tile=tile(1, "a", 1, "yellow"), row=0, column=0),
        Placement(tile=tile(2, "b", 1, "yellow"), row=1, column=1),
    )
    with pytest.raises(IllegalMove):
        formed_words(board, placements)


def test_formed_words_reject_collision() -> None:
    board = make_board(3, (None,) * 9)
    board = board.with_tiles({board.index(1, 1): tile(1, "a", 1, "yellow")})
    placements = (Placement(tile=tile(2, "b", 1, "yellow"), row=1, column=1),)
    with pytest.raises(IllegalMove):
        formed_words(board, placements)


def test_anchor_first_move_must_cover_center() -> None:
    board = make_board(3, (None,) * 9)
    placements = (Placement(tile=tile(1, "a", 1, "yellow"), row=0, column=0),)
    with pytest.raises(IllegalMove):
        validate_anchor(board, placements, opening_tiles=1, opening_covers_center=True)


def test_an_opening_stands_off_the_center_when_the_rules_let_it() -> None:
    board = make_board(3, (None,) * 9)
    placements = (Placement(tile=tile(1, "a", 1, "yellow"), row=0, column=0),)
    validate_anchor(board, placements, opening_tiles=1, opening_covers_center=False)


def test_an_opening_states_how_many_tiles_it_takes() -> None:
    board = make_board(3, (None,) * 9)
    placements = (Placement(tile=tile(1, "a", 1, "yellow"), row=1, column=1),)
    validate_anchor(board, placements, opening_tiles=1, opening_covers_center=True)
    with pytest.raises(IllegalMove, match="at least 2 tiles"):
        validate_anchor(board, placements, opening_tiles=2, opening_covers_center=True)


def test_anchor_requires_connection() -> None:
    board = make_board(3, (None,) * 9)
    board = board.with_tiles({board.index(0, 0): tile(1, "a", 1, "yellow")})
    placements = (Placement(tile=tile(2, "b", 1, "yellow"), row=2, column=2),)
    with pytest.raises(IllegalMove):
        validate_anchor(board, placements, opening_tiles=2, opening_covers_center=True)


def test_score_category_match() -> None:
    board = make_board(3, (None,) * 9)
    board = board.model_copy(
        update={
            "bonuses": (None,) * 4
            + (Bonus(kind=BonusKind.CATEGORY_MULTIPLIER, multiplier=3, category="red"),)
            + (None,) * 4
        }
    )
    board = board.with_tiles({board.index(1, 0): tile(1, "a", 1, "yellow")})
    placements = (Placement(tile=tile(2, "b", 5, "red"), row=1, column=1),)
    words = formed_words(board, placements)
    result = score_move(board, words, bingo=0)
    assert result.points == 16


def test_score_word_multiplier() -> None:
    board = make_board(3, (None,) * 9)
    board = board.model_copy(
        update={
            "bonuses": (None,) * 4
            + (Bonus(kind=BonusKind.WORD_MULTIPLIER, multiplier=2),)
            + (None,) * 4
        }
    )
    board = board.with_tiles({board.index(1, 0): tile(1, "a", 1, "yellow")})
    placements = (Placement(tile=tile(2, "b", 2, "yellow"), row=1, column=1),)
    words = formed_words(board, placements)
    result = score_move(board, words, bingo=0)
    assert result.points == 6


def test_score_letter_multiplier() -> None:
    board = make_board(3, (None,) * 9)
    board = board.model_copy(
        update={
            "bonuses": (None,) * 4
            + (Bonus(kind=BonusKind.LETTER_MULTIPLIER, multiplier=3),)
            + (None,) * 4
        }
    )
    board = board.with_tiles({board.index(1, 0): tile(1, "a", 1, "yellow")})
    placements = (Placement(tile=tile(2, "b", 2, "yellow"), row=1, column=1),)
    words = formed_words(board, placements)
    result = score_move(board, words, bingo=0)
    assert result.points == 7


def test_score_bingo_bonus() -> None:
    board = make_board(3, (None,) * 9)
    placements = (
        Placement(tile=tile(1, "a", 1, "yellow"), row=1, column=0),
        Placement(tile=tile(2, "b", 1, "yellow"), row=1, column=1),
    )
    words = formed_words(board, placements)
    result = score_move(board, words, bingo=50)
    assert result.bingo == 50
    assert result.points == 52


def test_validate_words_policy() -> None:
    absent = TextLexicon.from_words(["xyz"])
    words = formed_words(
        make_board(3, (None,) * 9),
        (
            Placement(tile=tile(1, "a", 1, "yellow"), row=1, column=0),
            Placement(tile=tile(2, "b", 1, "yellow"), row=1, column=1),
        ),
    )
    with pytest.raises(InvalidWord):
        validate_words(absent, words, validate=True)
    validate_words(absent, words, validate=False)
    present = TextLexicon.from_words(["ab"])
    validate_words(present, words, validate=True)


def test_exchange_apply_and_validate() -> None:
    position = empty_position()
    first = tile(1, "a", 1, "yellow")
    second = tile(2, "b", 2, "green")
    third = tile(3, "c", 3, "blue")
    position = position.model_copy(
        update={
            "state": position.state.model_copy(
                update={
                    "racks": {0: (first, second), 1: ()},
                    "bag": (third,),
                }
            )
        }
    )
    exchange = Exchange(tile_ids=(1,))
    validate_exchange(position, 0, exchange, limit=None, min_bag=1)
    updated = apply_exchange(position, 0, exchange)
    assert {t.identifier for t in updated.state.racks[0]} == {2, 3}
    assert updated.state.bag == (first,)


def test_exchange_limit() -> None:
    position = empty_position()
    position = position.model_copy(
        update={
            "state": position.state.model_copy(
                update={
                    "racks": {0: (tile(1, "a", 1, "yellow"),), 1: ()},
                    "bag": (tile(2, "b", 1, "yellow"),),
                    "exchange_counts": {0: 3, 1: 0},
                }
            )
        }
    )
    with pytest.raises(IllegalMove):
        validate_exchange(position, 0, Exchange(tile_ids=(1,)), limit=3, min_bag=1)


def test_final_scores() -> None:
    position = _scoring_position()
    assert _scored(position, went_out=0) == {0: 8, 1: 19}
    assert _scored(position, went_out=None) == {0: 7, 1: 19}
    assert _scored(position, went_out=0, going_out_award=False) == {0: 7, 1: 19}


def test_final_scores_leave_the_racks_alone_where_penalties_are_off() -> None:
    position = _scoring_position()
    assert _scored(position, went_out=None, rack_penalties=False) == {0: 10, 1: 20}
    assert _scored(position, went_out=0, rack_penalties=False) == {0: 11, 1: 20}


def test_a_flat_bonus_rewards_the_finisher_where_the_award_is_off() -> None:
    position = _scoring_position()
    assert _scored(
        position,
        went_out=0,
        going_out_award=False,
        going_out_bonus=20,
    ) == {0: 27, 1: 19}
    assert _scored(position, went_out=0, going_out_bonus=20) == {0: 28, 1: 19}
    assert _scored(position, went_out=None, going_out_bonus=20) == {0: 7, 1: 19}


def _scoring_position() -> Position:
    position = empty_position()
    return position.model_copy(
        update={
            "state": position.state.model_copy(
                update={
                    "racks": {0: (tile(1, "a", 3, "blue"),), 1: (tile(2, "b", 1, "yellow"),)},
                    "scores": {0: 10, 1: 20},
                }
            )
        }
    )


def _scored(
    position: Position,
    *,
    went_out: int | None,
    rack_penalties: bool = _PENALTIES_APPLY,
    going_out_award: bool = _AWARD_STANDS,
    going_out_bonus: int = _NO_FLAT_BONUS,
) -> dict[int, int]:
    return final_scores(
        position,
        went_out,
        rack_penalties=rack_penalties,
        going_out_award=going_out_award,
        going_out_bonus=going_out_bonus,
    )


def test_next_seat() -> None:
    assert next_seat((0, 1, 2), 0) == 1
    assert next_seat((0, 1, 2), 2) == 0
    assert next_seat((0,), 0) == 0


def test_next_seat_among_walks_past_the_seats_that_are_out() -> None:
    assert next_seat_among((0, 1, 2), 0, frozenset({0, 2})) == 2
    assert next_seat_among((0, 1, 2), 2, frozenset({2})) == 2
    assert next_seat_among((0, 1, 2), 0, frozenset()) == 1
