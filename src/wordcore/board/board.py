from __future__ import annotations

from pydantic import model_validator

from wordcore.board.bonus import Bonus
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Tile


class Board(BaseFrozen):
    size: int
    bonuses: tuple[Bonus | None, ...]
    tiles: tuple[Tile | None, ...]

    @model_validator(mode="after")
    def validate_dimensions(self) -> Board:
        expected = self.size * self.size
        if len(self.bonuses) != expected or len(self.tiles) != expected:
            raise ValueError("board arrays must match the square size")
        return self

    def index(self, row: int, column: int) -> int:
        return row * self.size + column

    def bonus_at(self, row: int, column: int) -> Bonus | None:
        return self.bonuses[self.index(row, column)]

    def tile_at(self, row: int, column: int) -> Tile | None:
        return self.tiles[self.index(row, column)]

    def in_bounds(self, row: int, column: int) -> bool:
        return 0 <= row < self.size and 0 <= column < self.size

    def is_empty(self) -> bool:
        return all(tile is None for tile in self.tiles)

    def center(self) -> int:
        return self.size // 2

    def with_tiles(
        self,
        replacements: dict[int, Tile | None],
    ) -> Board:
        tiles = list(self.tiles)
        for index, tile in replacements.items():
            tiles[index] = tile

        return self.model_copy(update={"tiles": tuple(tiles)})
