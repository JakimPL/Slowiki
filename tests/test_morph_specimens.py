from pathlib import Path

import pytest
import yaml

from lexica.morph.index import analyse_dictionary
from lexica.morph.sources.sgjp import analyse_word

try:
    import morfeusz2  # type: ignore[import-untyped]
except ImportError:
    morfeusz2 = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STRESS_PATH = PROJECT_ROOT / "tests" / "specimens" / "stress.yaml"

requires_morfeusz2 = pytest.mark.skipif(morfeusz2 is None, reason="morfeusz2 missing")

_Reference = tuple[str, str, str, list[str], list[str]]


def _read_stress() -> tuple[str, list[tuple[str, list[_Reference]]]]:
    document = yaml.safe_load(STRESS_PATH.read_text(encoding="utf-8"))
    dict_id = document["dict_id"]
    specimens: list[tuple[str, list[_Reference]]] = []
    for specimen in document["specimens"]:
        specimens.append((specimen["word"], specimen["analyses"]))
    return dict_id, specimens


@requires_morfeusz2
@pytest.mark.skipif(not STRESS_PATH.is_file(), reason="stress specimens missing")
def test_stress_specimens_match_reference_analyses() -> None:
    dict_id, specimens = _read_stress()
    analyzer = morfeusz2.Morfeusz()
    assert analyzer.dict_id() == dict_id
    for word, reference in specimens:
        expected = {
            (analysis[1].upper(), analysis[2])
            for analysis in reference
            if not analysis[2].startswith(("ign", "xx"))
        }
        actual = {(analysis.lemma, analysis.tag) for analysis in analyse_word(analyzer, word)}
        assert actual == expected, word


@requires_morfeusz2
@pytest.mark.skipif(not STRESS_PATH.is_file(), reason="stress specimens missing")
def test_stress_pipeline_builds_classes() -> None:
    _, specimens = _read_stress()
    words = tuple(word.upper() for (word, _) in specimens)
    analyzer = morfeusz2.Morfeusz()
    result = analyse_dictionary(words, analyzer, None)
    store = result.store

    assert len(store.entries["BRONIĄ"]) == 2
    zamek_ids = store.entries["ZAMEK"]
    assert len(zamek_ids) == 2
    assert {store.classes[class_id].base for class_id in zamek_ids} == {"ZAMEK"}

    for record in store.classes.values():
        assert record.base
        for variant in record.variants:
            assert variant.form

    for word, reference in specimens:
        surface = word.upper()
        has_real = any(not analysis[2].startswith(("ign", "xx")) for analysis in reference)
        if has_real:
            assert surface in store.entries, surface
        else:
            assert surface in store.unknown, surface
