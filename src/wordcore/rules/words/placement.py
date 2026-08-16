from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Tile


class Placement(BaseFrozen):
    tile: Tile
    row: int
    column: int
