from pathlib import Path
from typing import Annotated

from pydantic import Field

from wordcore.models.base import BaseFrozen
from wordtable.documents import read_named
from wordtable.names import PresetName
from wordtable.paths import CONFIGURATION_STYLES_PATH

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
    name: PresetName
    font_family: str
    light: ThemeTokens
    dark: ThemeTokens


def load_style_tokens(directory: Path, name: str) -> StyleTokens:
    return StyleTokens.model_validate(read_named(directory, CONFIGURATION_STYLES_PATH, name))
