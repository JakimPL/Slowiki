from pathlib import Path

import pytest
import yaml

from lexica.grammar.dialect import TagsetDialect
from lexica.grammar.parse import inflection_of
from lexica.lore.lookup import lore_of
from lexica.lore.sources import LoreSources
from lexica.sources.sgjp import analyse_word, build_morfeusz_engine
from wordcore.lexicon.lexicon import TextLexicon

try:
    import morfeusz2  # type: ignore[import-untyped]
except ImportError:
    morfeusz2 = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STRESS_PATH = PROJECT_ROOT / "tests" / "specimens" / "stress.yaml"

requires_morfeusz2 = pytest.mark.skipif(morfeusz2 is None, reason="morfeusz2 missing")
requires_stress = pytest.mark.skipif(not STRESS_PATH.is_file(), reason="stress specimens missing")

_Reference = tuple[str, str, str, list[str], list[str]]

_IGNORED = ("ign", "xx")


def _read_stress() -> tuple[str, list[tuple[str, list[_Reference]]]]:
    document = yaml.safe_load(STRESS_PATH.read_text(encoding="utf-8"))
    dict_id = document["dict_id"]
    specimens: list[tuple[str, list[_Reference]]] = []
    for specimen in document["specimens"]:
        specimens.append((specimen["word"], specimen["analyses"]))
    return dict_id, specimens


@requires_stress
def test_every_specimen_tag_reads_in_the_sgjp_tagset() -> None:
    _, specimens = _read_stress()
    tags = {analysis[2] for (_, reference) in specimens for analysis in reference}
    for tag in sorted(tags):
        inflection_of(tag, TagsetDialect.SGJP)


@requires_morfeusz2
@requires_stress
def test_stress_specimens_match_reference_analyses() -> None:
    dict_id, specimens = _read_stress()
    analyzer = build_morfeusz_engine()
    assert analyzer.dict_id() == dict_id
    for word, reference in specimens:
        expected = {
            (*_split_lemma(analysis[1]), analysis[2])
            for analysis in reference
            if not analysis[2].startswith(_IGNORED)
        }
        actual = {
            (analysis.lexeme.lemma, analysis.lexeme.pattern, analysis.tag)
            for analysis in analyse_word(analyzer, word)
        }
        assert actual == expected, word


@requires_morfeusz2
@requires_stress
def test_every_stress_specimen_reads_into_a_based_reading() -> None:
    _, specimens = _read_stress()
    words = tuple(word.upper() for (word, _) in specimens)
    sources = LoreSources(engine=build_morfeusz_engine(), rescue={})
    lexicon = TextLexicon.from_words(words)
    lore = {word: lore_of(sources, word, lexicon) for word in words}

    assert len(lore["BRONIĄ"].readings) == 2
    assert {reading.base for reading in lore["ZAMEK"].readings} == {"ZAMEK"}
    assert len(lore["ZAMEK"].readings) == 2

    for word, answer in lore.items():
        for reading in answer.readings:
            assert reading.base, word
            assert all(form.text for form in reading.forms), word

    for word, reference in specimens:
        surface = word.upper()
        read = any(not analysis[2].startswith(_IGNORED) for analysis in reference)
        assert (len(lore[surface].readings) > 0) is read, surface


def _split_lemma(lemma: str) -> tuple[str, str]:
    written, _, pattern = lemma.partition(":")
    return written.upper(), pattern
