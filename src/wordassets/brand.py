from typing import Final

from wordassets.drawing.node import Element
from wordassets.drawing.shapes import glyph, rect, svg
from wordassets.icons import icon_painting, painted_element
from wordassets.tiles import tile_group
from wordcore.tiles.tile import TilePreset
from wordtable.config import ThemeTokens

PRODUCT_NAME: Final = "Literabble"

_OG_WIDTH: Final = 1200.0
_OG_HEIGHT: Final = 630.0
_OG_TILE: Final = 130.0
_OG_TILE_GAP: Final = 14.0
_OG_WORD: Final = "SŁOWA"
_OG_NAME_SIZE: Final = 92.0
_OG_NAME_WEIGHT: Final = 900
_OG_NAME_DROP: Final = 0.74
_OG_TILES_DROP: Final = 0.24

_SPLASH_WIDTH: Final = 1080.0
_SPLASH_HEIGHT: Final = 1920.0
_SPLASH_ICON: Final = 640.0
_SPLASH_NAME_SIZE: Final = 84.0
_SPLASH_NAME_DROP: Final = 0.68


def og_image(theme: ThemeTokens, tiles: TilePreset) -> Element:
    by_symbol = {spec.symbol: spec for spec in tiles.letters}
    row_width = len(_OG_WORD) * _OG_TILE + (len(_OG_WORD) - 1) * _OG_TILE_GAP
    start = (_OG_WIDTH - row_width) / 2
    top = _OG_HEIGHT * _OG_TILES_DROP
    children: list[Element] = [
        rect(
            0,
            0,
            _OG_WIDTH,
            _OG_HEIGHT,
            fill=theme.chrome.surface,
            radius=None,
        )
    ]
    for offset, symbol in enumerate(_OG_WORD):
        spec = by_symbol[symbol]
        children.append(
            tile_group(
                start + offset * (_OG_TILE + _OG_TILE_GAP),
                top,
                _OG_TILE,
                spec.symbol,
                spec.value,
                spec.category,
                theme,
            )
        )
    children.append(
        glyph(
            _OG_WIDTH / 2,
            _OG_HEIGHT * _OG_NAME_DROP,
            PRODUCT_NAME,
            fill=theme.chrome.text,
            size=_OG_NAME_SIZE,
            weight=_OG_NAME_WEIGHT,
            anchor="middle",
        )
    )
    return svg(_OG_WIDTH, _OG_HEIGHT, tuple(children))


def splash(theme: ThemeTokens) -> Element:
    icon_x = (_SPLASH_WIDTH - _SPLASH_ICON) / 2
    icon_y = (_SPLASH_HEIGHT - _SPLASH_ICON) / 2 - _SPLASH_ICON / 4
    children: list[Element] = [
        rect(
            0,
            0,
            _SPLASH_WIDTH,
            _SPLASH_HEIGHT,
            fill=theme.chrome.surface,
            radius=None,
        )
    ]
    children.extend(
        _shifted(painted_element(paint), icon_x, icon_y)
        for paint in icon_painting(_SPLASH_ICON, theme, maskable=True)
    )
    children.append(
        glyph(
            _SPLASH_WIDTH / 2,
            _SPLASH_HEIGHT * _SPLASH_NAME_DROP,
            PRODUCT_NAME,
            fill=theme.chrome.text,
            size=_SPLASH_NAME_SIZE,
            weight=_OG_NAME_WEIGHT,
            anchor="middle",
        )
    )
    return svg(_SPLASH_WIDTH, _SPLASH_HEIGHT, tuple(children))


def _shifted(element: Element, x: float, y: float) -> Element:
    return Element(
        tag="g",
        attributes=(("transform", f"translate({x:g} {y:g})"),),
        children=(element,),
        text=None,
    )
