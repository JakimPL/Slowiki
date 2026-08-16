from wordcore.board.board import Board
from wordcore.board.bonus import Bonus, BonusKind
from wordcore.rules.words.placement import Placement
from wordcore.tiles.tile import Tile


def authored_score(
    board: Board, placements: tuple[Placement, ...]
) -> tuple[tuple[tuple[str, int], ...], int]:
    size = board.size
    combined_tiles = list(board.tiles)
    new_indices: set[int] = set()
    for placement in placements:
        index = board.index(placement.row, placement.column)
        combined_tiles[index] = placement.tile
        new_indices.add(index)
    combined = Board(size=size, bonuses=board.bonuses, tiles=tuple(combined_tiles))
    runs: list[tuple[int, ...]] = []
    for row in range(size):
        runs.extend(_row_runs(combined, row))
    for column in range(size):
        runs.extend(_column_runs(combined, column))
    words: list[tuple[str, int]] = []
    for run in runs:
        if not any(index in new_indices for index in run):
            continue
        cells = list(run)
        tiles = [_require(combined.tiles[index]) for index in cells]
        letter_sum = sum(
            _tile_points(tiles[offset], board.bonuses[cells[offset]], cells[offset] in new_indices)
            for offset in range(len(cells))
        )
        multiplier = 1
        for offset in range(len(cells)):
            if cells[offset] in new_indices:
                bonus = board.bonuses[cells[offset]]
                if bonus is not None and bonus.kind == BonusKind.WORD_MULTIPLIER:
                    multiplier *= bonus.multiplier
        text = "".join(tile.letter for tile in tiles)
        words.append((text, letter_sum * multiplier))
    total = sum(points for _, points in words)
    return tuple(sorted(words)), total


def _row_runs(combined: Board, row: int) -> list[tuple[int, ...]]:
    runs: list[tuple[int, ...]] = []
    current: list[int] = []
    for column in range(combined.size):
        index = combined.index(row, column)
        if combined.tiles[index] is not None:
            current.append(index)
        else:
            if len(current) >= 2:
                runs.append(tuple(current))
            current = []
    if len(current) >= 2:
        runs.append(tuple(current))
    return runs


def _column_runs(combined: Board, column: int) -> list[tuple[int, ...]]:
    runs: list[tuple[int, ...]] = []
    current: list[int] = []
    for row in range(combined.size):
        index = combined.index(row, column)
        if combined.tiles[index] is not None:
            current.append(index)
        else:
            if len(current) >= 2:
                runs.append(tuple(current))
            current = []
    if len(current) >= 2:
        runs.append(tuple(current))
    return runs


def _tile_points(tile: Tile, bonus: Bonus | None, is_new: bool) -> int:
    if not is_new or bonus is None:
        return tile.value
    if bonus.kind == BonusKind.LETTER_MULTIPLIER:
        return tile.value * bonus.multiplier
    if bonus.kind == BonusKind.CATEGORY_MULTIPLIER and tile.category == bonus.category:
        return tile.value * bonus.multiplier
    return tile.value


def _require(tile: Tile | None) -> Tile:
    assert tile is not None
    return tile
