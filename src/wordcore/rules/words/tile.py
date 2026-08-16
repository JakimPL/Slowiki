from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Tile


# TODO: what's the difference between Placement?
class WordTile(BaseFrozen):
    tile: Tile
    row: int
    column: int
