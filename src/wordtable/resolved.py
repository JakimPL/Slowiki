from wordcore.board.preset import BoardPreset
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tileset import TileSet
from wordtable.names import PresetName
from wordtable.rules import RulesConfig
from wordtable.scheme import SpecimenWord


class ResolvedScheme(BaseFrozen):
    scheme: PresetName
    specimen: SpecimenWord
    rules: RulesConfig
    board: BoardPreset
    tiles: TileSet
