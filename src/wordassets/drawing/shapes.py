from wordassets.drawing.node import Element

_FONT_STACK = "Lato, 'Segoe UI', sans-serif"


def svg(width: float, height: float, children: tuple[Element, ...]) -> Element:
    return Element(
        tag="svg",
        attributes=(
            ("xmlns", "http://www.w3.org/2000/svg"),
            ("viewBox", f"0 0 {formatted(width)} {formatted(height)}"),
            ("width", formatted(width)),
            ("height", formatted(height)),
        ),
        children=children,
        text=None,
    )


def rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str,
    radius: float | None,
) -> Element:
    attributes = [
        ("x", formatted(x)),
        ("y", formatted(y)),
        ("width", formatted(width)),
        ("height", formatted(height)),
        ("fill", fill),
    ]
    if radius is not None:
        attributes.append(("rx", formatted(radius)))

    return Element(
        tag="rect",
        attributes=tuple(attributes),
        children=(),
        text=None,
    )


def circle(
    center_x: float,
    center_y: float,
    radius: float,
    *,
    fill: str,
) -> Element:
    return Element(
        tag="circle",
        attributes=(
            ("cx", formatted(center_x)),
            ("cy", formatted(center_y)),
            ("r", formatted(radius)),
            ("fill", fill),
        ),
        children=(),
        text=None,
    )


def polygon(points: tuple[tuple[float, float], ...], *, fill: str) -> Element:
    joined = " ".join(f"{formatted(x)},{formatted(y)}" for x, y in points)
    return Element(
        tag="polygon",
        attributes=(("points", joined), ("fill", fill)),
        children=(),
        text=None,
    )


def group(children: tuple[Element, ...]) -> Element:
    return Element(
        tag="g",
        attributes=(),
        children=children,
        text=None,
    )


def glyph(
    x: float,
    y: float,
    content: str,
    *,
    fill: str,
    size: float,
    weight: int,
    anchor: str,
) -> Element:
    return Element(
        tag="text",
        attributes=(
            ("x", formatted(x)),
            ("y", formatted(y)),
            ("fill", fill),
            ("font-family", _FONT_STACK),
            ("font-size", formatted(size)),
            ("font-weight", str(weight)),
            ("text-anchor", anchor),
            ("dominant-baseline", "central"),
        ),
        children=(),
        text=content,
    )


def formatted(value: float) -> str:
    return f"{value:g}"
