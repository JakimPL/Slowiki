from wordcore.board.preset import BoardPreset
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tileset import TileSet
from wordgames.names import GameName
from wordtable.names import PresetName
from wordtable.rules import RulesConfig


class ResolvedScheme(BaseFrozen):
    scheme: PresetName
    game: GameName
    rules: RulesConfig
    board: BoardPreset
    tiles: TileSet
