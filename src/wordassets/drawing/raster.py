import math
from typing import Final, NamedTuple

from wordassets.colors import channels_of

_SUBROWS: Final = 4


class RoundedRectShape(NamedTuple):
    x: float
    y: float
    width: float
    height: float
    radius: float


class CircleShape(NamedTuple):
    center_x: float
    center_y: float
    radius: float


class PolygonShape(NamedTuple):
    points: tuple[tuple[float, float], ...]


Shape = RoundedRectShape | CircleShape | PolygonShape


class Painted(NamedTuple):
    shape: Shape
    color: str


def rendered_rows(
    width: int,
    height: int,
    background: str | None,
    paints: tuple[Painted, ...],
) -> list[bytearray]:
    base = _base_pixel(background)
    rows: list[bytearray] = []
    for row in range(height):
        pixels: list[list[float]] = [list(base) for _ in range(width)]
        for paint in paints:
            coverage = _row_coverage(paint.shape, row, width)
            if coverage is None:
                continue

            red, green, blue = channels_of(paint.color)
            for column, amount in coverage:
                _composite(pixels[column], (red, green, blue), amount)

        rows.append(_packed(pixels))

    return rows


def _base_pixel(background: str | None) -> tuple[float, float, float, float]:
    if background is None:
        return (0.0, 0.0, 0.0, 0.0)

    red, green, blue = channels_of(background)
    return (float(red), float(green), float(blue), 255.0)


def _composite(
    pixel: list[float],
    color: tuple[int, int, int],
    coverage: float,
) -> None:
    keep = 1 - coverage
    pixel[0] = color[0] * coverage + pixel[0] * keep
    pixel[1] = color[1] * coverage + pixel[1] * keep
    pixel[2] = color[2] * coverage + pixel[2] * keep
    pixel[3] = 255 * coverage + pixel[3] * keep


def _packed(pixels: list[list[float]]) -> bytearray:
    packed = bytearray()
    for pixel in pixels:
        packed.extend(round(channel) for channel in pixel)
    return packed


def _row_coverage(
    shape: Shape,
    row: int,
    width: int,
) -> list[tuple[int, float]] | None:
    amounts = [0.0] * width
    touched = False
    for subrow in range(_SUBROWS):
        y = row + (subrow + 0.5) / _SUBROWS
        for start, end in _spans_at(shape, y):
            touched = _accumulate(amounts, start, end, width) or touched

    if not touched:
        return None

    return [
        (
            column,
            amount / _SUBROWS,
        )
        for column, amount in enumerate(amounts)
        if amount > 0
    ]


def _accumulate(
    amounts: list[float],
    start: float,
    end: float,
    width: int,
) -> bool:
    left = max(start, 0.0)
    right = min(end, float(width))
    if right <= left:
        return False

    first = int(left)
    last = min(math.ceil(right), width)
    for column in range(first, last):
        overlap = min(right, column + 1.0) - max(left, float(column))
        if overlap > 0:
            amounts[column] += overlap
    return True


def _spans_at(shape: Shape, y: float) -> list[tuple[float, float]]:
    if isinstance(shape, CircleShape):
        return _circle_spans(shape, y)

    if isinstance(shape, RoundedRectShape):
        return _rounded_rect_spans(shape, y)

    return _polygon_spans(shape, y)


def _circle_spans(shape: CircleShape, y: float) -> list[tuple[float, float]]:
    offset = y - shape.center_y
    if abs(offset) >= shape.radius:
        return []

    reach = math.sqrt(shape.radius**2 - offset**2)
    return [(shape.center_x - reach, shape.center_x + reach)]


def _rounded_rect_spans(
    shape: RoundedRectShape,
    y: float,
) -> list[tuple[float, float]]:
    if y <= shape.y or y >= shape.y + shape.height:
        return []

    radius = min(shape.radius, shape.width / 2, shape.height / 2)
    top_zone = shape.y + radius
    bottom_zone = shape.y + shape.height - radius
    if top_zone <= y <= bottom_zone:
        return [(shape.x, shape.x + shape.width)]

    center_y = top_zone if y < top_zone else bottom_zone
    offset = y - center_y
    reach = math.sqrt(max(radius**2 - offset**2, 0.0))
    left = shape.x + radius - reach
    right = shape.x + shape.width - radius + reach
    return [(left, right)]


def _polygon_spans(
    shape: PolygonShape,
    y: float,
) -> list[tuple[float, float]]:
    crossings: list[float] = []
    points = shape.points
    for index, (start_x, start_y) in enumerate(points):
        end_x, end_y = points[(index + 1) % len(points)]
        if (start_y <= y < end_y) or (end_y <= y < start_y):
            fraction = (y - start_y) / (end_y - start_y)
            crossings.append(start_x + fraction * (end_x - start_x))

    crossings.sort()
    return [
        (
            crossings[index],
            crossings[index + 1],
        )
        for index in range(0, len(crossings) - 1, 2)
    ]
