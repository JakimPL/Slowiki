import tomllib
from collections.abc import Mapping, Sequence
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Final, NamedTuple

from lexica.artifact.formats import ARTIFACT_FORMATS
from lexica.artifact.kind import ArtifactKind
from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.paths import dictionary_archive, dictionary_compiled

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
DOCUMENT: Final[Path] = PROJECT_ROOT / "docs" / "lexicon-contract.md"
MANIFEST: Final[Path] = PROJECT_ROOT / "pyproject.toml"

KINDS_SECTION: Final = "Kinds"
ENVELOPE_SECTION: Final = "Envelope"
BOUNDARIES_SECTION: Final = "Boundaries"

RESERVED: Final = "—"
STEM_PLACEHOLDER: Final = "{stem}"
ARCHIVE_SUFFIX: Final = ".zip"

_HEADING: Final = "## "
_PIPE: Final = "|"
_FENCE: Final = "`"
_KIND_COLUMNS: Final = 6
_PAIR_COLUMNS: Final = 2
_TABLE_PREAMBLE: Final = 2
_ROLES: Final = ("producer", "reader", "consumer")


class KindRow(NamedTuple):
    kind: str
    format: int
    file_name: str
    producer: str
    reader: str
    consumer: str


def main(document: Path, manifest: Path) -> None:
    rows = kind_rows(document)
    _ensure_kinds_declared(document, rows)
    for row in rows:
        _ensure_format_agrees(document, row)
        _ensure_file_name_agrees(document, row)
        _ensure_members_resolve(document, row)

    for constant, declared in constant_values(document).items():
        _ensure_constant_agrees(document, constant, declared)

    for boundary, contract in boundary_contracts(document).items():
        _ensure_contract_declared(document, manifest, boundary, contract)

    print(f"{document}: {len(rows)} kinds agree with the code")


def kind_rows(document: Path) -> tuple[KindRow, ...]:
    return tuple(_kind_row(document, cells) for cells in table(document, KINDS_SECTION))


def constant_values(document: Path) -> Mapping[str, str]:
    return _pairs(document, ENVELOPE_SECTION)


def boundary_contracts(document: Path) -> Mapping[str, str]:
    return _pairs(document, BOUNDARIES_SECTION)


def table(document: Path, section: str) -> tuple[tuple[str, ...], ...]:
    lines = _table_lines(document, section)
    return tuple(_cells(line) for line in lines[_TABLE_PREAMBLE:])


def contract_names(manifest: Path) -> tuple[str, ...]:
    loaded = tomllib.loads(manifest.read_text(encoding="utf-8"))
    contracts = loaded["tool"]["importlinter"]["contracts"]
    return tuple(str(contract["name"]) for contract in contracts)


def _pairs(document: Path, section: str) -> Mapping[str, str]:
    rows = table(document, section)
    for cells in rows:
        _ensure_columns(document, section, cells, _PAIR_COLUMNS)

    return {cells[0]: cells[1] for cells in rows}


def _kind_row(document: Path, cells: tuple[str, ...]) -> KindRow:
    _ensure_columns(document, KINDS_SECTION, cells, _KIND_COLUMNS)
    kind, declared, file_name, producer, reader, consumer = cells
    return KindRow(
        kind=kind,
        format=_parsed_format(document, kind, declared),
        file_name=file_name,
        producer=producer,
        reader=reader,
        consumer=consumer,
    )


def _table_lines(document: Path, section: str) -> tuple[str, ...]:
    lines = document.read_text(encoding="utf-8").splitlines()
    collected: list[str] = []
    for line in lines[_section_start(document, section, lines) :]:
        if line.startswith(_PIPE):
            collected.append(line)
        elif len(collected) > 0 or line.startswith(_HEADING):
            break

    _ensure_table_present(document, section, collected)
    return tuple(collected)


def _section_start(document: Path, section: str, lines: Sequence[str]) -> int:
    heading = f"{_HEADING}{section}"
    for index, line in enumerate(lines):
        if line.strip() == heading:
            return index + 1

    raise InvalidConfiguration(f"{document}: the section {section} is missing")


def _cells(line: str) -> tuple[str, ...]:
    return tuple(_plain(cell) for cell in line.strip().strip(_PIPE).split(_PIPE))


def _plain(cell: str) -> str:
    return cell.strip().strip(_FENCE)


def _parsed_format(document: Path, kind: str, declared: str) -> int:
    if not declared.isdigit():
        raise InvalidConfiguration(f"{document}: {kind} declares {declared}, which names no format")

    return int(declared)


def _member(document: Path, subject: str, dotted: str) -> object:
    module_name, _, attribute = dotted.rpartition(".")
    if len(module_name) == 0:
        raise InvalidConfiguration(f"{document}: {subject} {dotted} names no module")

    values = vars(_module(document, subject, module_name))
    if attribute not in values:
        raise InvalidConfiguration(f"{document}: {subject} {dotted} is absent from the code")

    return values[attribute]


def _module(document: Path, subject: str, module_name: str) -> ModuleType:
    try:
        return import_module(module_name)
    except ModuleNotFoundError as error:
        raise InvalidConfiguration(
            f"{document}: {subject} names the missing module {module_name}"
        ) from error


def _text_of(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")

    return str(value)


def _ensure_kinds_declared(document: Path, rows: tuple[KindRow, ...]) -> None:
    declared = tuple(row.kind for row in rows)
    _ensure_rows_distinct(document, declared)
    known = {kind.value for kind in ArtifactKind}
    missing = sorted(known - set(declared))
    if len(missing) > 0:
        raise InvalidConfiguration(f"{document}: the artifact kind {missing[0]} carries no row")

    unknown = sorted(set(declared) - known)
    if len(unknown) > 0:
        raise InvalidConfiguration(f"{document}: the row {unknown[0]} names no artifact kind")


def _ensure_rows_distinct(document: Path, declared: tuple[str, ...]) -> None:
    seen: set[str] = set()
    for kind in declared:
        if kind in seen:
            raise InvalidConfiguration(f"{document}: the kind {kind} carries more than one row")

        seen.add(kind)


def _ensure_format_agrees(document: Path, row: KindRow) -> None:
    current = ARTIFACT_FORMATS[ArtifactKind(row.kind)]
    if row.format != current:
        raise InvalidConfiguration(
            f"{document}: {row.kind} declares format {row.format} "
            f"where the code carries format {current}"
        )


def _ensure_file_name_agrees(document: Path, row: KindRow) -> None:
    kind = ArtifactKind(row.kind)
    for name in DictionaryName:
        stem = dictionary_archive(name).name.removesuffix(ARCHIVE_SUFFIX)
        declared = row.file_name.replace(STEM_PLACEHOLDER, stem)
        produced = dictionary_compiled(name, kind).name
        if produced != declared:
            raise InvalidConfiguration(
                f"{document}: {name} yields {produced} where the contract declares {declared}"
            )


def _ensure_members_resolve(document: Path, row: KindRow) -> None:
    members = (row.producer, row.reader, row.consumer)
    for role, dotted in zip(_ROLES, members, strict=True):
        if dotted != RESERVED:
            _member(document, f"the {row.kind} {role}", dotted)


def _ensure_constant_agrees(document: Path, constant: str, declared: str) -> None:
    present = _text_of(_member(document, "the envelope constant", constant))
    if present != declared:
        raise InvalidConfiguration(
            f"{document}: {constant} holds {present} where the contract declares {declared}"
        )


def _ensure_contract_declared(document: Path, manifest: Path, boundary: str, contract: str) -> None:
    if contract not in contract_names(manifest):
        raise InvalidConfiguration(
            f"{document}: {boundary} names the import contract {contract}, "
            f"which {manifest} leaves undeclared"
        )


def _ensure_columns(document: Path, section: str, cells: tuple[str, ...], expected: int) -> None:
    if len(cells) != expected:
        raise InvalidConfiguration(
            f"{document}: a row of {section} carries {len(cells)} columns where {expected} belong"
        )


def _ensure_table_present(document: Path, section: str, collected: Sequence[str]) -> None:
    if len(collected) <= _TABLE_PREAMBLE:
        raise InvalidConfiguration(f"{document}: the section {section} carries no table")


if __name__ == "__main__":
    main(DOCUMENT, MANIFEST)
