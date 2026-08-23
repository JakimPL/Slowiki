import marshal
from pathlib import Path
from typing import Final, NoReturn

from lexica.artifact.envelope import read_envelope, write_envelope
from lexica.artifact.formats import ARTIFACT_FORMATS
from lexica.artifact.header import ArtifactHeader
from lexica.artifact.kind import ArtifactKind
from lexica.lore.rescue import RescueRow, RescueTable
from wordcore.errors.exceptions import InvalidConfiguration

_ROW_FIELDS: Final = 4


def write_rescue_table(table: RescueTable, destination: Path) -> None:
    header = ArtifactHeader(
        kind=ArtifactKind.RESCUE,
        format=ARTIFACT_FORMATS[ArtifactKind.RESCUE],
        entries=len(table),
    )
    write_envelope(destination, header, marshal.dumps(_plain_rows(table)))


def read_rescue_table(path: Path) -> RescueTable:
    header, body = read_envelope(path, ArtifactKind.RESCUE)
    table = _decoded_table(path, body)
    _ensure_entries(path, header, table)
    return table


def _plain_rows(table: RescueTable) -> dict[str, tuple[tuple[str, str, str, str], ...]]:
    return {
        surface: tuple((row.lemma, row.tag, row.name, row.label) for row in rows)
        for surface, rows in table.items()
    }


def _decoded_table(path: Path, body: bytes) -> dict[str, tuple[RescueRow, ...]]:
    decoded = _decoded_body(path, body)
    if not isinstance(decoded, dict):
        _refuse_shape(path)

    return {_surface_of(path, surface): _rows_of(path, rows) for surface, rows in decoded.items()}


def _decoded_body(path: Path, body: bytes) -> object:
    try:
        return marshal.loads(body)
    except (EOFError, ValueError) as error:
        raise InvalidConfiguration(
            f"{path} holds a damaged rescue table; delete the file and rebuild it"
        ) from error


def _surface_of(path: Path, surface: object) -> str:
    if not isinstance(surface, str):
        _refuse_shape(path)

    return surface


def _rows_of(path: Path, rows: object) -> tuple[RescueRow, ...]:
    if not isinstance(rows, tuple):
        _refuse_shape(path)

    return tuple(_row_of(path, row) for row in rows)


def _row_of(path: Path, row: object) -> RescueRow:
    if not isinstance(row, tuple) or len(row) != _ROW_FIELDS:
        _refuse_shape(path)

    if not all(isinstance(field, str) for field in row):
        _refuse_shape(path)

    lemma, tag, name, label = row
    return RescueRow(lemma=lemma, tag=tag, name=name, label=label)


def _refuse_shape(path: Path) -> NoReturn:
    raise InvalidConfiguration(f"{path} holds a rescue table of an unreadable shape")


def _ensure_entries(path: Path, header: ArtifactHeader, table: RescueTable) -> None:
    if len(table) != header.entries:
        raise InvalidConfiguration(
            f"{path} declares {header.entries} surfaces and holds {len(table)}; "
            "delete the file and rebuild it"
        )
