from wordassets.colors import mixed_hex
from wordassets.drawing.node import Element
from wordassets.drawing.shapes import glyph, group, rect
from wordassets.geometry import band_height, tile_radius
from wordtable.style import ThemeTokens

_LETTER_SIZE_RATIO = 0.52
_VALUE_SIZE_RATIO = 0.24
_LETTER_WEIGHT = 900
_VALUE_WEIGHT = 600
_LETTER_RISE_RATIO = 0.44
_VALUE_INSET_RATIO = 0.16
_BAND_INSET_RATIO = 0.5


def tile_group(
    x: float,
    y: float,
    side: float,
    symbol: str,
    value: int,
    category: str,
    theme: ThemeTokens,
) -> Element:
    band = theme.tiles.bands.get(category)
    face = (
        theme.tiles.face
        if band is None
        else mixed_hex(theme.tiles.face, band, theme.tiles.face_tint)
    )
    radius = tile_radius(side)
    band_size = band_height(side)
    inset = radius * _BAND_INSET_RATIO
    children = [rect(x, y, side, side, fill=face, radius=radius)]
    if band is not None:
        children.append(
            rect(
                x + inset,
                y + side - band_size,
                side - inset * 2,
                band_size - inset,
                fill=band,
                radius=band_size / 3,
            )
        )
    children.append(
        glyph(
            x + side / 2,
            y + side * _LETTER_RISE_RATIO,
            symbol,
            fill=theme.tiles.text,
            size=side * _LETTER_SIZE_RATIO,
            weight=_LETTER_WEIGHT,
            anchor="middle",
        )
    )
    if value > 0:
        children.append(
            glyph(
                x + side * (1 - _VALUE_INSET_RATIO),
                y + side * (1 - 2 * _VALUE_INSET_RATIO),
                str(value),
                fill=theme.tiles.text,
                size=side * _VALUE_SIZE_RATIO,
                weight=_VALUE_WEIGHT,
                anchor="end",
            )
        )
    return group(tuple(children))
