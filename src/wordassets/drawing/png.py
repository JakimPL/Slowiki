import struct
import zlib
from typing import Final

_SIGNATURE: Final = b"\x89PNG\r\n\x1a\n"
_RGBA_DEPTH: Final = 8
_RGBA_COLOR_TYPE: Final = 6


def png_bytes(width: int, height: int, rows: list[bytearray]) -> bytes:
    header = struct.pack(">IIBBBBB", width, height, _RGBA_DEPTH, _RGBA_COLOR_TYPE, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    return (
        _SIGNATURE
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(raw))
        + _chunk(b"IEND", b"")
    )


def _chunk(kind: bytes, body: bytes) -> bytes:
    checksum = zlib.crc32(kind + body)
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", checksum)
