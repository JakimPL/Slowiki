from typing import Final

_HEX_BASE: Final = 16
_CHANNEL_WIDTH: Final = 2


def mixed_hex(base: str, tint: str, fraction: float) -> str:
    blended = tuple(
        round(base_channel + (tint_channel - base_channel) * fraction)
        for base_channel, tint_channel in zip(channels_of(base), channels_of(tint), strict=True)
    )
    return "#" + "".join(f"{channel:02X}" for channel in blended)


def channels_of(color: str) -> tuple[int, int, int]:
    body = color.removeprefix("#")
    red, green, blue = (
        int(body[offset : offset + _CHANNEL_WIDTH], _HEX_BASE)
        for offset in range(0, len(body), _CHANNEL_WIDTH)
    )
    return red, green, blue
