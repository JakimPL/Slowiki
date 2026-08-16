from wordcore.board.board import Board, BonusKind
from wordcore.board.preset import board_from_preset
from wordtable.catalogue import resolve_scheme
from wordtable.paths import CONFIG_DIR


def load_board(scheme: str) -> Board:
    resolved = resolve_scheme(CONFIG_DIR, scheme)
    return board_from_preset(resolved.board)


def bonus_counts(board: Board) -> dict[tuple[str, int, str | None], int]:
    counts: dict[tuple[str, int, str | None], int] = {}
    for bonus in board.bonuses:
        if bonus is None:
            continue
        key = (bonus.kind.value, bonus.multiplier, bonus.category)
        counts[key] = counts.get(key, 0) + 1
    return counts


def test_literaki_bonus_counts() -> None:
    board = load_board("literaki")
    assert bonus_counts(board) == {
        ("category_multiplier", 3, "red"): 17,
        ("category_multiplier", 3, "green"): 24,
        ("category_multiplier", 3, "blue"): 8,
        ("category_multiplier", 3, "yellow"): 20,
        ("word_multiplier", 2, None): 16,
        ("word_multiplier", 3, None): 8,
    }


def test_literaki_center_is_red() -> None:
    board = load_board("literaki")
    bonus = board.bonus_at(7, 7)
    assert bonus is not None
    assert bonus.kind == BonusKind.CATEGORY_MULTIPLIER
    assert bonus.category == "red"


def test_literaki_diagonal_symmetry() -> None:
    board = load_board("literaki")
    for row in range(board.size):
        for column in range(board.size):
            assert board.bonus_at(row, column) == board.bonus_at(column, row)


def test_scrabble_bonus_counts() -> None:
    board = load_board("scrabble")
    assert bonus_counts(board) == {
        ("word_multiplier", 3, None): 8,
        ("word_multiplier", 2, None): 17,
        ("letter_multiplier", 3, None): 12,
        ("letter_multiplier", 2, None): 24,
    }


def test_scrabble_center_is_double_word() -> None:
    board = load_board("scrabble")
    bonus = board.bonus_at(7, 7)
    assert bonus is not None
    assert bonus.kind == BonusKind.WORD_MULTIPLIER
    assert bonus.multiplier == 2
