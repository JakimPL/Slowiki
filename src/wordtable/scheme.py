from pathlib import Path
from typing import Annotated

from pydantic import StringConstraints

from wordcore.models.base import BaseFrozen
from wordtable.documents import read_named
from wordtable.names import PresetName
from wordtable.paths import CONFIGURATION_SCHEMES_PATH
from wordtable.rules import RulesConfig

SpecimenWord = Annotated[str, StringConstraints(to_upper=True, min_length=1)]


class SchemeConfig(BaseFrozen):
    name: PresetName
    specimen: SpecimenWord
    rules: RulesConfig


def load_scheme(directory: Path, name: str) -> SchemeConfig:
    return SchemeConfig.model_validate(read_named(directory, CONFIGURATION_SCHEMES_PATH, name))
