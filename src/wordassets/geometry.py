import math
from typing import Final

TILE_RADIUS_RATIO: Final = 1 / 7
BAND_RATIO: Final = 1 / 7

_STAR_INNER_RATIO: Final = 0.4


def tile_radius(side: float) -> float:
    return side * TILE_RADIUS_RATIO


def band_height(side: float) -> float:
    return side * BAND_RATIO


def star_points(
    center_x: float,
    center_y: float,
    radius: float,
) -> tuple[tuple[float, float], ...]:
    inner = radius * _STAR_INNER_RATIO
    diagonal = inner / math.sqrt(2)
    return (
        (center_x, center_y - radius),
        (center_x + diagonal, center_y - diagonal),
        (center_x + radius, center_y),
        (center_x + diagonal, center_y + diagonal),
        (center_x, center_y + radius),
        (center_x - diagonal, center_y + diagonal),
        (center_x - radius, center_y),
        (center_x - diagonal, center_y - diagonal),
    )
