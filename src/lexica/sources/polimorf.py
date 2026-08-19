import gzip
from pathlib import Path

from lexica.lore.analysis import Analysis, analysis_of
from lexica.lore.analysis_source import AnalysisSource

_FIELDS = 4


def rescue_analyses(
    polimorf_path: Path,
    target_forms: frozenset[str],
) -> dict[str, tuple[Analysis, ...]]:
    rows: dict[str, set[tuple[str, str, str]]] = {}
    with gzip.open(polimorf_path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < _FIELDS:
                continue
            form, lemma, tag, label = fields[0], fields[1], fields[2], fields[3]
            if form not in target_forms:
                continue
            rows.setdefault(form, set()).add((lemma, tag, label))

    rescued: dict[str, tuple[Analysis, ...]] = {}
    for form, interpretations in rows.items():
        rescued[form] = tuple(
            analysis_of(form.upper(), lemma, tag, AnalysisSource.POLIMORF, (label,), ())
            for (lemma, tag, label) in sorted(interpretations)
        )
    return rescued
