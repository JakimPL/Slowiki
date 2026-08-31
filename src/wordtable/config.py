from pathlib import Path
from typing import Annotated

from pydantic import Field

from wordcore.models.base import BaseFrozen
from wordtable.documents import read_mapping
from wordtable.names import PresetName

PositiveSeconds = Annotated[float, Field(gt=0)]


class ServiceConfig(BaseFrozen):
    host: str
    port: int


class TablesConfig(BaseFrozen):
    life_seconds: PositiveSeconds
    linger_seconds: PositiveSeconds
    sweep_seconds: PositiveSeconds
    premove_delay_seconds: PositiveSeconds


class Configuration(BaseFrozen):
    service: ServiceConfig
    tables: TablesConfig
    scheme: PresetName
    style: PresetName


def read_config(path: Path) -> Configuration:
    return Configuration.model_validate(read_mapping(path))
