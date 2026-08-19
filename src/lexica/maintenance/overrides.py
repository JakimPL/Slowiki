from pathlib import Path

import yaml

from wordcore.errors.exceptions import InvalidConfiguration

_LEMMA_KEY: str = "lemma"
_TAG_KEY: str = "tag"
_FORM_KEY: str = "form"
_ANALYSES_KEY: str = "analyses"


def parse_overrides(path: Path, words: frozenset[str]) -> dict[str, tuple[tuple[str, str], ...]]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or "overrides" not in document:
        raise InvalidConfiguration(f"malformed overrides file: {path}")
    entries = document["overrides"]
    if not isinstance(entries, list):
        raise InvalidConfiguration(f"malformed overrides file: {path}")

    overrides: dict[str, tuple[tuple[str, str], ...]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise InvalidConfiguration(f"malformed overrides file: {path}")
        form = entry.get(_FORM_KEY)
        analyses = entry.get(_ANALYSES_KEY)
        if not isinstance(form, str) or not isinstance(analyses, list):
            raise InvalidConfiguration(f"malformed overrides file: {path}")
        surface = form.upper()
        if surface not in words:
            raise InvalidConfiguration(f"override form absent from the dictionary: {surface}")
        if surface in overrides:
            raise InvalidConfiguration(f"duplicate override form: {surface}")

        rows: set[tuple[str, str]] = set()
        for analysis in analyses:
            if not isinstance(analysis, dict):
                raise InvalidConfiguration(f"malformed overrides file: {path}")
            lemma = analysis.get(_LEMMA_KEY)
            tag = analysis.get(_TAG_KEY)
            if not isinstance(lemma, str) or not isinstance(tag, str):
                raise InvalidConfiguration(f"malformed overrides file: {path}")
            rows.add((lemma.upper(), tag))
        overrides[surface] = tuple(sorted(rows))

    return overrides
