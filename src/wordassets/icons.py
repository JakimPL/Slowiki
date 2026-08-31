from typing import Final

from wordassets.drawing.ico import ico_bytes
from wordassets.drawing.node import Element
from wordassets.drawing.png import png_bytes
from wordassets.drawing.raster import (
    CircleShape,
    Painted,
    PolygonShape,
    RoundedRectShape,
    Shape,
    rendered_rows,
)
from wordassets.drawing.shapes import circle, polygon, rect, svg
from wordassets.geometry import band_height, star_points, tile_radius
from wordtable.style import ThemeTokens

_TILE_RATIO: Final = 0.66
_MASKABLE_TILE_RATIO: Final = 0.5
_STAR_RADIUS_RATIO: Final = 0.26
_STAR_RISE_RATIO: Final = 0.42
_BAND_INSET_RATIO: Final = 0.5
_BAND_ORDER: Final = ("yellow", "green", "blue", "red")
_BAND_GAP: Final = 2.0
_FAVICON_SIZES: Final = (16, 32, 48)


def icon_painting(
    size: float,
    theme: ThemeTokens,
    *,
    maskable: bool,
) -> tuple[Painted, ...]:
    tile_side = size * (_MASKABLE_TILE_RATIO if maskable else _TILE_RATIO)
    x = (size - tile_side) / 2
    y = (size - tile_side) / 2
    radius = tile_radius(tile_side)
    paints = [
        Painted(
            RoundedRectShape(x, y, tile_side, tile_side, radius),
            theme.tiles.face,
        ),
        *_band_segments(x, y, tile_side, theme),
        Painted(
            PolygonShape(
                star_points(
                    x + tile_side / 2,
                    y + tile_side * _STAR_RISE_RATIO,
                    tile_side * _STAR_RADIUS_RATIO,
                )
            ),
            theme.board.star,
        ),
    ]
    return tuple(paints)


def icon_svg_element(
    size: float,
    theme: ThemeTokens,
    *,
    maskable: bool,
) -> Element:
    background = rect(
        0,
        0,
        size,
        size,
        fill=theme.chrome.surface,
        radius=None,
    )
    painted = tuple(
        painted_element(paint)
        for paint in icon_painting(
            size,
            theme,
            maskable=maskable,
        )
    )
    return svg(size, size, (background, *painted))


def icon_png_bytes(size: int, theme: ThemeTokens, *, maskable: bool) -> bytes:
    rows = rendered_rows(
        size,
        size,
        theme.chrome.surface,
        icon_painting(size, theme, maskable=maskable),
    )
    return png_bytes(size, size, rows)


def favicon_ico_bytes(theme: ThemeTokens) -> bytes:
    images = [(size, icon_png_bytes(size, theme, maskable=False)) for size in _FAVICON_SIZES]
    return ico_bytes(images)


def _band_segments(
    x: float,
    y: float,
    side: float,
    theme: ThemeTokens,
) -> list[Painted]:
    inset = tile_radius(side) * _BAND_INSET_RATIO
    band = band_height(side)
    total = side - 2 * inset
    segment = (total - _BAND_GAP * (len(_BAND_ORDER) - 1)) / len(_BAND_ORDER)
    top = y + side - band
    return [
        Painted(
            RoundedRectShape(
                x + inset + offset * (segment + _BAND_GAP),
                top,
                segment,
                band - inset,
                (band - inset) / 3,
            ),
            theme.tiles.bands[category],
        )
        for offset, category in enumerate(_BAND_ORDER)
    ]


def painted_element(painted: Painted) -> Element:
    return _shape_element(painted.shape, painted.color)


def _shape_element(shape: Shape, fill: str) -> Element:
    if isinstance(shape, RoundedRectShape):
        return rect(
            shape.x,
            shape.y,
            shape.width,
            shape.height,
            fill=fill,
            radius=shape.radius,
        )

    if isinstance(shape, CircleShape):
        return circle(
            shape.center_x,
            shape.center_y,
            shape.radius,
            fill=fill,
        )

    return polygon(shape.points, fill=fill)
