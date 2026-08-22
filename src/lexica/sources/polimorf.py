import gzip
from pathlib import Path
from typing import Final, NamedTuple

from lexica.lore.analysis import Analysis, analysis_of
from lexica.lore.analysis_source import AnalysisSource

FIELD_SEPARATOR: Final = "\t"

_FIELDS: Final = 5


class PolimorfRow(NamedTuple):
    form: str
    lemma: str
    tag: str
    name: str
    labels: str


Reading = tuple[str, str, str, str]


def rescue_analyses(
    polimorf_path: Path,
    target_forms: frozenset[str],
) -> dict[str, tuple[Analysis, ...]]:
    readings = _matching_readings(polimorf_path, target_forms)
    return {
        surface: tuple(
            analysis_of(surface, lemma, tag, AnalysisSource.POLIMORF, (name,), (labels,))
            for (lemma, tag, name, labels) in sorted(interpretations)
        )
        for surface, interpretations in readings.items()
    }


def _matching_readings(
    polimorf_path: Path,
    target_forms: frozenset[str],
) -> dict[str, set[Reading]]:
    readings: dict[str, set[Reading]] = {}
    with gzip.open(polimorf_path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            row = _row_of(line)
            if row is None:
                continue
            surface = row.form.upper()
            if surface not in target_forms:
                continue
            readings.setdefault(surface, set()).add((row.lemma, row.tag, row.name, row.labels))
    return readings


def _row_of(line: str) -> PolimorfRow | None:
    fields = line.rstrip("\r\n").split(FIELD_SEPARATOR)
    if len(fields) != _FIELDS:
        return None
    form, lemma, tag, name, labels = fields
    return PolimorfRow(form=form, lemma=lemma, tag=tag, name=name, labels=labels)
