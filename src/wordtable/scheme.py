from pathlib import Path

from wordcore.models.base import BaseFrozen
from wordgames.names import GameName
from wordtable.documents import read_named
from wordtable.names import PresetName
from wordtable.paths import CONFIGURATION_SCHEMES_PATH
from wordtable.rules import RulesConfig


class SchemeConfig(BaseFrozen):
    name: PresetName
    game: GameName
    rules: RulesConfig


def load_scheme(directory: Path, name: str) -> SchemeConfig:
    return SchemeConfig.model_validate(read_named(directory, CONFIGURATION_SCHEMES_PATH, name))
