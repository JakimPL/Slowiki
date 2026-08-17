from typing import Final

from wordcore.board.board import Board
from wordcore.errors.exceptions import IllegalMove
from wordcore.models.base import BaseFrozen
from wordcore.rules.words.placement import Placement, board_with_placements
from wordcore.tiles.tile import Tile

_NEIGHBORS: Final = ((-1, 0), (1, 0), (0, -1), (0, 1))


class FormedWord(BaseFrozen):
    tiles: tuple[Placement, ...]
    text: str
    new_indices: frozenset[int]


def formed_words(
    board: Board,
    placements: tuple[Placement, ...],
) -> tuple[FormedWord, ...]:
    _ensure_any_placement(placements)
    _ensure_distinct_squares(board, placements)
    _ensure_within_board(board, placements)
    _ensure_free_squares(board, placements)
    combined = board_with_placements(board, placements)
    new_indices = frozenset(
        board.index(
            placement.row,
            placement.column,
        )
        for placement in placements
    )
    if len(placements) == 1:
        return _single_tile_words(combined, placements[0], new_indices)

    return _straight_words(combined, placements, new_indices)


def validate_anchor(board: Board, placements: tuple[Placement, ...]) -> None:
    if board.is_empty():
        _ensure_opening_size(placements)
        _ensure_covers_center(board, placements)
        return

    _ensure_touches_existing(board, placements)


def _ensure_any_placement(placements: tuple[Placement, ...]) -> None:
    if not placements:
        raise IllegalMove("a play requires at least one tile")


def _ensure_distinct_squares(
    board: Board,
    placements: tuple[Placement, ...],
) -> None:
    squares = {board.index(placement.row, placement.column) for placement in placements}
    if len(squares) != len(placements):
        raise IllegalMove("placements overlap")


def _ensure_within_board(
    board: Board,
    placements: tuple[Placement, ...],
) -> None:
    for placement in placements:
        if not board.in_bounds(placement.row, placement.column):
            raise IllegalMove("placement is outside the board")


def _ensure_free_squares(
    board: Board,
    placements: tuple[Placement, ...],
) -> None:
    for placement in placements:
        if board.tile_at(placement.row, placement.column) is not None:
            raise IllegalMove("placement collides with an existing tile")


def _single_tile_words(
    combined: Board,
    placement: Placement,
    new_indices: frozenset[int],
) -> tuple[FormedWord, ...]:
    across = _line_word(
        combined,
        placement.row,
        placement.column,
        horizontal=True,
    )
    down = _line_word(
        combined,
        placement.column,
        placement.row,
        horizontal=False,
    )
    words = [
        _to_word(
            line,
            new_indices,
        )
        for line in (across, down)
        if line is not None
    ]
    if not words:
        raise IllegalMove("a play must form a word")

    return tuple(words)


def _straight_words(
    combined: Board,
    placements: tuple[Placement, ...],
    new_indices: frozenset[int],
) -> tuple[FormedWord, ...]:
    rows = {placement.row for placement in placements}
    columns = {placement.column for placement in placements}
    if len(rows) == 1:
        return _axis_words(
            combined,
            next(iter(rows)),
            placements,
            new_indices,
            horizontal=True,
        )

    if len(columns) == 1:
        return _axis_words(
            combined,
            next(iter(columns)),
            placements,
            new_indices,
            horizontal=False,
        )

    raise IllegalMove("placements must share a row or a column")


def _axis_words(
    combined: Board,
    fixed: int,
    placements: tuple[Placement, ...],
    new_indices: frozenset[int],
    *,
    horizontal: bool,
) -> tuple[FormedWord, ...]:
    low, high = _placement_bounds(placements, horizontal)
    _ensure_contiguous(combined, fixed, low, high, horizontal)
    span = _line_span(combined, fixed, low, high, horizontal)
    main = _to_word(_line_tiles(combined, fixed, span, horizontal), new_indices)
    return (main, *_cross_words(combined, placements, new_indices, horizontal))


def _cross_words(
    combined: Board,
    placements: tuple[Placement, ...],
    new_indices: frozenset[int],
    horizontal: bool,
) -> tuple[FormedWord, ...]:
    words: list[FormedWord] = []
    for placement in placements:
        line = _cross_line(combined, placement, horizontal)
        if line is None:
            continue

        word = _to_word(line, new_indices)
        if word not in words:
            words.append(word)

    return tuple(words)


def _cross_line(
    combined: Board,
    placement: Placement,
    horizontal: bool,
) -> tuple[Placement, ...] | None:
    if horizontal:
        return _line_word(
            combined,
            placement.column,
            placement.row,
            horizontal=False,
        )

    return _line_word(
        combined,
        placement.row,
        placement.column,
        horizontal=True,
    )


def _line_word(
    combined: Board,
    fixed: int,
    at: int,
    *,
    horizontal: bool,
) -> tuple[Placement, ...] | None:
    start, end = _line_span(combined, fixed, at, at, horizontal)
    if start == end:
        return None

    return _line_tiles(combined, fixed, (start, end), horizontal)


def _line_span(
    combined: Board,
    fixed: int,
    low: int,
    high: int,
    horizontal: bool,
) -> tuple[int, int]:
    start = low
    while start > 0 and _tile_on_line(combined, fixed, start - 1, horizontal) is not None:
        start -= 1

    end = high
    while (
        end < combined.size - 1 and _tile_on_line(combined, fixed, end + 1, horizontal) is not None
    ):
        end += 1

    return start, end


def _line_tiles(
    combined: Board,
    fixed: int,
    span: tuple[int, int],
    horizontal: bool,
) -> tuple[Placement, ...]:
    start, end = span
    tiles: list[Placement] = []
    for coordinate in range(start, end + 1):
        tile = _tile_on_line(combined, fixed, coordinate, horizontal)
        if tile is None:
            raise IllegalMove("word contains a gap")

        row, column = _square_on_line(fixed, coordinate, horizontal)
        tiles.append(Placement(tile=tile, row=row, column=column))

    return tuple(tiles)


def _square_on_line(
    fixed: int,
    coordinate: int,
    horizontal: bool,
) -> tuple[int, int]:
    if horizontal:
        return fixed, coordinate

    return coordinate, fixed


def _tile_on_line(
    combined: Board,
    fixed: int,
    coordinate: int,
    horizontal: bool,
) -> Tile | None:
    row, column = _square_on_line(fixed, coordinate, horizontal)
    return combined.tile_at(row, column)


def _placement_bounds(
    placements: tuple[Placement, ...],
    horizontal: bool,
) -> tuple[int, int]:
    positions = [placement.column if horizontal else placement.row for placement in placements]
    return min(positions), max(positions)


def _ensure_contiguous(
    combined: Board,
    fixed: int,
    low: int,
    high: int,
    horizontal: bool,
) -> None:
    for coordinate in range(low, high + 1):
        if _tile_on_line(combined, fixed, coordinate, horizontal) is None:
            raise IllegalMove("placements leave a gap")


def _to_word(
    tiles: tuple[Placement, ...],
    new_indices: frozenset[int],
) -> FormedWord:
    return FormedWord(
        tiles=tiles,
        text="".join(placement.tile.letter for placement in tiles),
        new_indices=new_indices,
    )


def _ensure_opening_size(placements: tuple[Placement, ...]) -> None:
    if len(placements) < 2:
        raise IllegalMove("the first move requires at least two tiles")


def _ensure_covers_center(
    board: Board,
    placements: tuple[Placement, ...],
) -> None:
    center = board.center()
    if not any(placement.row == center and placement.column == center for placement in placements):
        raise IllegalMove("the first move must cover the center square")


def _ensure_touches_existing(
    board: Board,
    placements: tuple[Placement, ...],
) -> None:
    if any(
        _has_neighbor(
            board,
            placement.row,
            placement.column,
        )
        for placement in placements
    ):
        return

    raise IllegalMove("the play must connect to existing tiles")


def _has_neighbor(board: Board, row: int, column: int) -> bool:
    for delta_row, delta_column in _NEIGHBORS:
        neighbor_row = row + delta_row
        neighbor_column = column + delta_column
        if board.in_bounds(neighbor_row, neighbor_column) and (
            board.tile_at(neighbor_row, neighbor_column) is not None
        ):
            return True

    return False
