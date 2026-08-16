from wordcore.board.board import Board
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Tile


class Placement(BaseFrozen):
    tile: Tile
    row: int
    column: int


def board_with_placements(board: Board, placements: tuple[Placement, ...]) -> Board:
    return board.with_tiles(
        {board.index(placement.row, placement.column): placement.tile for placement in placements}
    )
