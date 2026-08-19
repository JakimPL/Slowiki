import gzip
from pathlib import Path

from lexica.morph.mapping import build_analysis
from lexica.morph.models import Analysis, MorphSource


def rescue_rows(
    polimorf_path: Path,
    target_forms: frozenset[str],
) -> dict[str, tuple[tuple[str, str], ...]]:
    rows: dict[str, set[tuple[str, str]]] = {}
    with gzip.open(polimorf_path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            form, lemma, tag = parts[0], parts[1], parts[2]
            if form not in target_forms:
                continue
            rows.setdefault(form, set()).add((lemma.upper(), tag))

    return {form: tuple(sorted(pairs)) for form, pairs in rows.items()}


def rescue_analyses(
    polimorf_path: Path,
    target_forms: frozenset[str],
) -> dict[str, tuple[Analysis, ...]]:
    rows: dict[str, set[tuple[str, str, str]]] = {}
    with gzip.open(polimorf_path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            form, lemma, tag = parts[0], parts[1], parts[2]
            if form not in target_forms:
                continue
            qualifier = parts[3] if len(parts) > 3 else ""
            rows.setdefault(form, set()).add((lemma, tag, qualifier))

    rescued: dict[str, tuple[Analysis, ...]] = {}
    for form, interpretations in rows.items():
        rescued[form] = tuple(
            build_analysis(
                form.upper(),
                lemma.upper(),
                tag,
                MorphSource.POLIMORF,
                (qualifier,) if qualifier else (),
            )
            for (lemma, tag, qualifier) in sorted(interpretations)
        )
    return rescued
