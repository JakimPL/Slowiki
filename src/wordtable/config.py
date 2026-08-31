from pathlib import Path
from typing import Annotated

from pydantic import Field, model_validator

from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordcore.models.letters import CanonicalSymbol, TileCount
from wordgames.names import GameName
from wordtable.documents import read_mapping
from wordtable.paths import (
    CONFIGURATION_SCHEMES_PATH,
    CONFIGURATION_STYLES_PATH,
    configuration_file,
)
from wordtable.presets.adjustment import LetterAdjustment

PositiveSeconds = Annotated[float, Field(gt=0)]
RackSize = Annotated[int, Field(ge=1, le=99)]


class ServiceConfig(BaseFrozen):
    host: str
    port: int


class TablesConfig(BaseFrozen):
    life_seconds: PositiveSeconds
    linger_seconds: PositiveSeconds
    sweep_seconds: PositiveSeconds


class TimeConfig(BaseFrozen):
    per_turn_seconds: int | None
    increment_seconds: int
    total_seconds: int | None
    premove_delay_seconds: float


class SchemeConfig(BaseFrozen):
    game: GameName
    board: str
    alphabet: str
    distribution: str
    dictionary: DictionaryName
    min_players: int
    max_players: int
    rack_size: RackSize | None
    blanks: TileCount
    letters: dict[CanonicalSymbol, LetterAdjustment]
    validate_on_play: bool
    premoves: bool
    exchange_limit: int | None
    exchange_min_bag: int
    pass_allowed: bool
    time: TimeConfig
    pass_end_rounds: int | None
    scoreless_end_limit: int | None
    bingo_bonus: int

    @model_validator(mode="after")
    def _ensure_end_limit(self) -> "SchemeConfig":
        if (
            self.max_players > 1
            and self.pass_end_rounds is None
            and self.scoreless_end_limit is None
        ):
            raise InvalidConfiguration(
                "a scheme seating several players needs pass_end_rounds or scoreless_end_limit"
            )

        return self


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
    tables: TablesConfig
    scheme: str
    style: str


def read_config(path: Path) -> Configuration:
    return Configuration.model_validate(read_mapping(path))


def load_scheme(directory: Path, name: str) -> SchemeConfig:
    path = directory / configuration_file(CONFIGURATION_SCHEMES_PATH, name)
    return SchemeConfig.model_validate(read_mapping(path))


def load_style_tokens(directory: Path, name: str) -> StyleTokens:
    path = directory / configuration_file(CONFIGURATION_STYLES_PATH, name)
    data = read_mapping(path)
    return StyleTokens.model_validate({**data, "name": name})
