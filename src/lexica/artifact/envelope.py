from pathlib import Path
from typing import BinaryIO, Final

from pydantic import ValidationError

from lexica.artifact.formats import ARTIFACT_FORMATS
from lexica.artifact.header import ArtifactHeader
from lexica.artifact.kind import ArtifactKind
from wordcore.errors.exceptions import InvalidConfiguration

MAGIC: Final = b"LITERABBLE"
LENGTH_BYTES: Final = 4
LENGTH_ORDER: Final = "big"
PARTIAL_SUFFIX: Final = ".partial"


def write_envelope(destination: Path, header: ArtifactHeader, body: bytes) -> None:
    encoded = header.model_dump_json().encode("utf-8")
    partial = destination.with_name(destination.name + PARTIAL_SUFFIX)
    partial.write_bytes(MAGIC + len(encoded).to_bytes(LENGTH_BYTES, LENGTH_ORDER) + encoded + body)
    partial.replace(destination)


def read_header(path: Path) -> ArtifactHeader:
    with path.open("rb") as stream:
        return _read_header(path, stream)


def read_envelope(path: Path, kind: ArtifactKind) -> tuple[ArtifactHeader, bytes]:
    with path.open("rb") as stream:
        header = _read_header(path, stream)
        _ensure_kind(path, header, kind)
        _ensure_format(path, header)
        return header, stream.read()


def _read_header(path: Path, stream: BinaryIO) -> ArtifactHeader:
    _ensure_magic(path, stream.read(len(MAGIC)))
    length = _header_length(path, stream.read(LENGTH_BYTES))
    return _decode_header(path, stream.read(length))


def _ensure_magic(path: Path, marker: bytes) -> None:
    if marker != MAGIC:
        raise InvalidConfiguration(
            f"{path} carries no artifact header; delete the file and rebuild it"
        )


def _header_length(path: Path, raw: bytes) -> int:
    if len(raw) != LENGTH_BYTES:
        raise InvalidConfiguration(f"{path} ends inside its artifact header")

    return int.from_bytes(raw, LENGTH_ORDER)


def _decode_header(path: Path, raw: bytes) -> ArtifactHeader:
    try:
        return ArtifactHeader.model_validate_json(raw)
    except ValidationError as error:
        raise InvalidConfiguration(f"{path} carries an unreadable artifact header") from error


def _ensure_kind(path: Path, header: ArtifactHeader, kind: ArtifactKind) -> None:
    if header.kind is not kind:
        raise InvalidConfiguration(
            f"{path} holds a {header.kind} artifact where a {kind} artifact belongs"
        )


def _ensure_format(path: Path, header: ArtifactHeader) -> None:
    current = ARTIFACT_FORMATS[header.kind]
    if header.format != current:
        raise InvalidConfiguration(
            f"{path} holds {header.kind} format {header.format} where format {current} belongs; "
            "delete the file and rebuild it"
        )
