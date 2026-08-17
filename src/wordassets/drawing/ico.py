import struct
from typing import Final

_ICON_TYPE: Final = 1
_HEADER_SIZE: Final = 6
_ENTRY_SIZE: Final = 16
_FULL_RANGE: Final = 256


def ico_bytes(images: list[tuple[int, bytes]]) -> bytes:
    header = struct.pack("<HHH", 0, _ICON_TYPE, len(images))
    entries = b""
    blobs = b""
    offset = _HEADER_SIZE + _ENTRY_SIZE * len(images)
    for size, blob in images:
        stamp = size % _FULL_RANGE
        entries += struct.pack(
            "<BBBBHHII",
            stamp,
            stamp,
            0,
            0,
            1,
            32,
            len(blob),
            offset,
        )
        blobs += blob
        offset += len(blob)

    return header + entries + blobs
