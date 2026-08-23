from collections.abc import Callable
from pathlib import Path
from typing import Final

import yaml

from lexica.lore.override import OverrideRow, OverrideTable
from wordcore.errors.exceptions import InvalidConfiguration

OVERRIDES_KEY: Final = "overrides"
FORM_KEY: Final = "form"
ANALYSES_KEY: Final = "analyses"
LEMMA_KEY: Final = "lemma"
TAG_KEY: Final = "tag"

Holds = Callable[[str], bool]


def parse_overrides(path: Path, holds: Holds) -> OverrideTable:
    entries = _entries(path)
    overrides: dict[str, tuple[OverrideRow, ...]] = {}
    for entry in entries:
        surface, rows = _entry(path, entry)
        _ensure_form_known(surface, holds)
        _ensure_form_unclaimed(surface, overrides)
        overrides[surface] = rows

    return overrides


def _entries(path: Path) -> list[object]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or OVERRIDES_KEY not in document:
        raise InvalidConfiguration(f"malformed overrides file: {path}")

    entries = document[OVERRIDES_KEY]
    if not isinstance(entries, list):
        raise InvalidConfiguration(f"malformed overrides file: {path}")

    return entries


def _entry(path: Path, entry: object) -> tuple[str, tuple[OverrideRow, ...]]:
    if not isinstance(entry, dict):
        raise InvalidConfiguration(f"malformed overrides file: {path}")

    form = entry.get(FORM_KEY)
    analyses = entry.get(ANALYSES_KEY)
    if not isinstance(form, str) or not isinstance(analyses, list):
        raise InvalidConfiguration(f"malformed overrides file: {path}")

    rows = {_row(path, analysis) for analysis in analyses}
    return form.upper(), tuple(sorted(rows))


def _row(path: Path, analysis: object) -> OverrideRow:
    if not isinstance(analysis, dict):
        raise InvalidConfiguration(f"malformed overrides file: {path}")

    lemma = analysis.get(LEMMA_KEY)
    tag = analysis.get(TAG_KEY)
    if not isinstance(lemma, str) or not isinstance(tag, str):
        raise InvalidConfiguration(f"malformed overrides file: {path}")

    return OverrideRow(lemma=lemma.upper(), tag=tag)


def _ensure_form_known(surface: str, holds: Holds) -> None:
    if not holds(surface):
        raise InvalidConfiguration(f"override form absent from the dictionary: {surface}")


def _ensure_form_unclaimed(surface: str, overrides: OverrideTable) -> None:
    if surface in overrides:
        raise InvalidConfiguration(f"duplicate override form: {surface}")
