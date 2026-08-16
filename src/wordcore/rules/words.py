from wordcore.board.board import Board
from wordcore.exceptions import IllegalMove
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Tile


class Placement(BaseFrozen):
    tile: Tile
    row: int
    column: int


class WordTile(BaseFrozen):
    tile: Tile
    row: int
    column: int


class FormedWord(BaseFrozen):
    tiles: tuple[WordTile, ...]
    text: str
    new_indices: frozenset[int]


def formed_words(board: Board, placements: tuple[Placement, ...]) -> tuple[FormedWord, ...]:
    if not placements:
        raise IllegalMove("a play requires at least one tile")
    if len({board.index(p.row, p.column) for p in placements}) != len(placements):
        raise IllegalMove("placements overlap")
    for placement in placements:
        if not board.in_bounds(placement.row, placement.column):
            raise IllegalMove("placement is outside the board")
        if board.tile_at(placement.row, placement.column) is not None:
            raise IllegalMove("placement collides with an existing tile")
    combined = board.with_tiles({board.index(p.row, p.column): p.tile for p in placements})
    new_indices = frozenset(board.index(p.row, p.column) for p in placements)
    if len(placements) == 1:
        placement = placements[0]
        words: list[FormedWord] = []
        horizontal = _horizontal(combined, placement.row, placement.column)
        if horizontal is not None:
            words.append(_to_word(horizontal, new_indices))
        vertical = _vertical(combined, placement.row, placement.column)
        if vertical is not None:
            words.append(_to_word(vertical, new_indices))
        if not words:
            raise IllegalMove("a play must form a word")
        return tuple(words)
    rows = {p.row for p in placements}
    columns = {p.column for p in placements}
    if len(rows) == 1:
        return _axis_words(combined, next(iter(rows)), placements, new_indices, True)
    if len(columns) == 1:
        return _axis_words(combined, next(iter(columns)), placements, new_indices, False)
    raise IllegalMove("placements must share a row or a column")


def _axis_words(
    combined: Board,
    fixed: int,
    placements: tuple[Placement, ...],
    new_indices: frozenset[int],
    horizontal: bool,
) -> tuple[FormedWord, ...]:
    positions = [p.column if horizontal else p.row for p in placements]
    low = min(positions)
    high = max(positions)
    for coordinate in range(low, high + 1):
        tile = (
            combined.tile_at(fixed, coordinate)
            if horizontal
            else combined.tile_at(coordinate, fixed)
        )
        if tile is None:
            raise IllegalMove("placements leave a gap")
    main = _word_along(combined, fixed, low, high, horizontal)
    words: list[FormedWord] = [_to_word(main, new_indices)]
    for placement in placements:
        cross = (
            _vertical(combined, placement.row, placement.column)
            if horizontal
            else _horizontal(combined, placement.row, placement.column)
        )
        if cross is not None:
            word = _to_word(cross, new_indices)
            if word not in words:
                words.append(word)
    return tuple(words)


def _word_along(
    combined: Board, fixed: int, low: int, high: int, horizontal: bool
) -> tuple[WordTile, ...]:
    start = low
    while start > 0:
        previous = (
            combined.tile_at(fixed, start - 1) if horizontal else combined.tile_at(start - 1, fixed)
        )
        if previous is None:
            break
        start -= 1
    end = high
    while end < combined.size - 1:
        following = (
            combined.tile_at(fixed, end + 1) if horizontal else combined.tile_at(end + 1, fixed)
        )
        if following is None:
            break
        end += 1
    tiles: list[WordTile] = []
    for coordinate in range(start, end + 1):
        tile = (
            combined.tile_at(fixed, coordinate)
            if horizontal
            else combined.tile_at(coordinate, fixed)
        )
        if tile is None:
            raise IllegalMove("word contains a gap")
        if horizontal:
            tiles.append(WordTile(tile=tile, row=fixed, column=coordinate))
        else:
            tiles.append(WordTile(tile=tile, row=coordinate, column=fixed))
    return tuple(tiles)


def _horizontal(combined: Board, row: int, column: int) -> tuple[WordTile, ...] | None:
    start = column
    while start > 0 and combined.tile_at(row, start - 1) is not None:
        start -= 1
    end = column
    while end < combined.size - 1 and combined.tile_at(row, end + 1) is not None:
        end += 1
    if end - start + 1 < 2:
        return None
    tiles: list[WordTile] = []
    for coordinate in range(start, end + 1):
        tile = combined.tile_at(row, coordinate)
        if tile is None:
            raise IllegalMove("word contains a gap")
        tiles.append(WordTile(tile=tile, row=row, column=coordinate))
    return tuple(tiles)


def _vertical(combined: Board, row: int, column: int) -> tuple[WordTile, ...] | None:
    start = row
    while start > 0 and combined.tile_at(start - 1, column) is not None:
        start -= 1
    end = row
    while end < combined.size - 1 and combined.tile_at(end + 1, column) is not None:
        end += 1
    if end - start + 1 < 2:
        return None
    tiles: list[WordTile] = []
    for coordinate in range(start, end + 1):
        tile = combined.tile_at(coordinate, column)
        if tile is None:
            raise IllegalMove("word contains a gap")
        tiles.append(WordTile(tile=tile, row=coordinate, column=column))
    return tuple(tiles)


def _to_word(tiles: tuple[WordTile, ...], new_indices: frozenset[int]) -> FormedWord:
    return FormedWord(
        tiles=tiles,
        text="".join(word_tile.tile.letter for word_tile in tiles),
        new_indices=new_indices,
    )


def validate_anchor(board: Board, placements: tuple[Placement, ...]) -> None:
    if board.is_empty():
        center = board.center()
        if len(placements) < 2:
            raise IllegalMove("the first move requires at least two tiles")
        if not any(p.row == center and p.column == center for p in placements):
            raise IllegalMove("the first move must cover the center square")
        return
    if any(_has_neighbor(board, p.row, p.column) for p in placements):
        return
    raise IllegalMove("the play must connect to existing tiles")


def _has_neighbor(board: Board, row: int, column: int) -> bool:
    for delta_row, delta_column in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        neighbor_row = row + delta_row
        neighbor_column = column + delta_column
        if board.in_bounds(neighbor_row, neighbor_column):
            if board.tile_at(neighbor_row, neighbor_column) is not None:
                return True
    return False
