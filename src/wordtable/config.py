from pathlib import Path
from typing import Any

import yaml

from wordcore.board.preset import BoardPreset
from wordcore.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import TilePreset


class ServiceConfig(BaseFrozen):
    host: str
    port: int


class TimeConfig(BaseFrozen):
    per_turn_seconds: int | None
    increment_seconds: int
    total_seconds: int | None


class SchemeConfig(BaseFrozen):
    game: str
    board: str
    tiles: str
    dictionary: str
    min_players: int
    max_players: int
    validate_on_play: bool
    premoves: bool
    exchange_limit: int | None
    pass_allowed: bool
    time: TimeConfig
    pass_end_limit: int | None
    scoreless_end_limit: int | None
    bingo_bonus: int


class StyleConfig(BaseFrozen):
    name: str
    board_color: str
    text_color: str
    tile_colors: dict[str, str]
    premium_colors: dict[str, str]


class Configuration(BaseFrozen):
    service: ServiceConfig
    scheme: str
    style: str


def read_config(path: Path) -> Configuration:
    return Configuration.model_validate(_read_yaml(path))


def load_scheme(directory: Path, name: str) -> SchemeConfig:
    return SchemeConfig.model_validate(_read_yaml(directory / "schemes" / f"{name}.yaml"))


def load_board_preset(directory: Path, name: str) -> BoardPreset:
    data = _read_yaml(directory / "presets" / "boards" / f"{name}.yaml")
    return BoardPreset.model_validate({**data, "name": name})


def load_tile_preset(directory: Path, name: str) -> TilePreset:
    data = _read_yaml(directory / "presets" / "tiles" / f"{name}.yaml")
    return TilePreset.model_validate({**data, "name": name})


def load_style(directory: Path, name: str) -> StyleConfig:
    data = _read_yaml(directory / "styles" / f"{name}.yaml")
    return StyleConfig.model_validate({**data, "name": name})


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise InvalidConfiguration(f"missing config file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise InvalidConfiguration(f"config file must contain a mapping: {path}")
    return data
