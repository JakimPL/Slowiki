from pathlib import Path
from typing import Annotated, Any

import yaml
from pydantic import Field

from lexica.names import DictionaryName
from wordcore.board.preset import BoardPreset
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import TilePreset
from wordgames.names import GameName
from wordtable.paths import (
    CONFIGURATION_BOARDS_PATH,
    CONFIGURATION_SCHEMES_PATH,
    CONFIGURATION_STYLES_PATH,
    CONFIGURATION_TILES_PATH,
    configuration_file,
)


class ServiceConfig(BaseFrozen):
    host: str
    port: int


class TimeConfig(BaseFrozen):
    per_turn_seconds: int | None
    increment_seconds: int
    total_seconds: int | None


class SchemeConfig(BaseFrozen):
    game: GameName
    board: str
    tiles: str
    dictionary: DictionaryName
    min_players: int
    max_players: int
    validate_on_play: bool
    premoves: bool
    exchange_limit: int | None
    exchange_min_bag: int
    pass_allowed: bool
    time: TimeConfig
    pass_end_limit: int | None
    scoreless_end_limit: int | None
    bingo_bonus: int


HexColor = Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")]
TintFraction = Annotated[float, Field(ge=0, le=1)]


class ChromeTokens(BaseFrozen):
    surface: HexColor
    panel: HexColor
    edge: HexColor
    text: HexColor
    muted: HexColor


class BoardTokens(BaseFrozen):
    surface: HexColor
    grid: HexColor
    frame: HexColor
    star: HexColor
    premium_label_share: TintFraction


class PremiumTokens(BaseFrozen):
    fill: HexColor
    label: HexColor


class TileTokens(BaseFrozen):
    face: HexColor
    edge: HexColor
    text: HexColor
    face_tint: TintFraction
    bands: dict[str, HexColor]


class AccentTokens(BaseFrozen):
    primary: HexColor
    on_primary: HexColor
    danger: HexColor
    success: HexColor
    premove: HexColor


class ThemeTokens(BaseFrozen):
    chrome: ChromeTokens
    board: BoardTokens
    premiums: dict[str, PremiumTokens]
    category_premiums: dict[str, PremiumTokens]
    tiles: TileTokens
    accents: AccentTokens


class StyleTokens(BaseFrozen):
    name: str
    font_family: str
    light: ThemeTokens
    dark: ThemeTokens


class Configuration(BaseFrozen):
    service: ServiceConfig
    scheme: str
    style: str


def read_config(path: Path) -> Configuration:
    return Configuration.model_validate(_read_yaml(path))


def load_scheme(directory: Path, name: str) -> SchemeConfig:
    path = directory / configuration_file(CONFIGURATION_SCHEMES_PATH, name)
    return SchemeConfig.model_validate(_read_yaml(path))


def load_board_preset(directory: Path, name: str) -> BoardPreset:
    path = directory / configuration_file(CONFIGURATION_BOARDS_PATH, name)
    data = _read_yaml(path)
    return BoardPreset.model_validate({**data, "name": name})


def load_tile_preset(directory: Path, name: str) -> TilePreset:
    path = directory / configuration_file(CONFIGURATION_TILES_PATH, name)
    data = _read_yaml(path)
    return TilePreset.model_validate({**data, "name": name})


def load_style_tokens(directory: Path, name: str) -> StyleTokens:
    path = directory / configuration_file(CONFIGURATION_STYLES_PATH, name)
    data = _read_yaml(path)
    return StyleTokens.model_validate({**data, "name": name})


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise InvalidConfiguration(f"missing config file: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise InvalidConfiguration(f"config file must contain a mapping: {path}")

    return data
