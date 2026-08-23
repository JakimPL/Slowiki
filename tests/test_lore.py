import pytest
from tests.fixtures.engines import NO_OVERRIDES, scripted_sources

from lexica.grammar.case import Case
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.lore.lookup import lore_of
from lexica.lore.override import OverrideRow, OverrideTable
from lexica.lore.reading import WordLore
from lexica.lore.rescue import RescueRow, RescueTable
from lexica.lore.sources import LoreSources
from lexica.names import DictionaryName
from lexica.sources.coverage import morphology_covers
from lexica.sources.sgjp import Interpretation, build_morfeusz_engine
from wordcore.lexicon.lexicon import TextLexicon

try:
    import morfeusz2  # type: ignore[import-untyped]
except ImportError:
    morfeusz2 = None

requires_morfeusz2 = pytest.mark.skipif(morfeusz2 is None, reason="morfeusz2 missing")

KOT_PARADIGM: list[Interpretation] = [
    ("kot", "kot:Sm1", "subst:sg:nom:m1", [], []),
    ("kota", "kot:Sm1", "subst:sg:gen.acc:m1", [], []),
    ("kotowi", "kot:Sm1", "subst:sg:dat:m1", [], []),
]


def _sources(
    answers: dict[str, list[Interpretation]],
    paradigms: dict[str, list[Interpretation]],
    rescue: RescueTable,
    overrides: OverrideTable = NO_OVERRIDES,
) -> LoreSources:
    return scripted_sources(answers, paradigms, rescue, overrides)


def _kot_lore(*dictionary: str) -> WordLore:
    sources = _sources(
        {"kot": [("kot", "kot:Sm1", "subst:sg:nom:m1", [], [])]},
        {"kot:Sm1": KOT_PARADIGM},
        {},
    )
    return lore_of(sources, "KOT", TextLexicon.from_words(dictionary))


def test_a_reading_carries_the_whole_generated_paradigm() -> None:
    lore = _kot_lore("KOT", "KOTA")
    assert lore.word == "KOT"
    assert lore.playable is True
    reading = lore.readings[0]
    assert reading.lexeme == "rzeczownik:KOT:Sm1"
    assert reading.part is PartOfSpeech.RZECZOWNIK
    assert reading.base == "KOT"
    assert {form.text for form in reading.forms} == {"KOT", "KOTA", "KOTOWI"}


def test_a_form_the_dictionary_lacks_stands_outside_play() -> None:
    membership = {form.text: form.playable for form in _kot_lore("KOT", "KOTA").readings[0].forms}
    assert membership == {"KOT": True, "KOTA": True, "KOTOWI": False}


def test_the_asked_form_carries_the_case_the_tag_states() -> None:
    reading = _kot_lore("KOT").readings[0]
    nominative = next(form for form in reading.forms if form.text == "KOT")
    assert nominative.tags.cases == frozenset({Case.MIANOWNIK})


def test_a_word_outside_the_dictionary_answers_unplayable() -> None:
    assert _kot_lore("PIES").playable is False


def test_a_word_no_source_reads_answers_no_reading() -> None:
    lore = lore_of(_sources({}, {}, {}), "AALBORSCY", TextLexicon.from_words(["AALBORSCY"]))
    assert lore.playable is True
    assert lore.readings == ()


def test_a_rescued_surface_earns_a_reading_holding_the_forms_the_source_states() -> None:
    rescue = {
        "ABBOZZO": (
            RescueRow(
                lemma="abbozzo",
                tag="subst:sg:nom.acc.voc:n:ncol",
                name="nazwa_pospolita",
                label="",
            ),
        )
    }
    lore = lore_of(_sources({}, {}, rescue), "ABBOZZO", TextLexicon.from_words(["ABBOZZO"]))
    reading = lore.readings[0]
    assert reading.lexeme == "rzeczownik:ABBOZZO:"
    assert [form.text for form in reading.forms] == ["ABBOZZO"]


def test_an_override_answers_the_reading_it_states() -> None:
    overrides = {"AALBORSCY": (OverrideRow(lemma="AALBORSKI", tag="adj:pl:nom.voc:m1:pos"),)}
    lore = lore_of(
        _sources({}, {}, {}, overrides),
        "AALBORSCY",
        TextLexicon.from_words(["AALBORSCY"]),
    )
    reading = lore.readings[0]
    assert reading.lexeme == "przymiotnik:AALBORSKI:"
    assert [form.text for form in reading.forms] == ["AALBORSCY"]


def test_an_override_wins_over_the_sources() -> None:
    overrides = {"KOT": (OverrideRow(lemma="KOT", tag="interj"),)}
    sources = _sources(
        {"kot": [("kot", "kot:Sm1", "subst:sg:nom:m1", [], [])]},
        {"kot:Sm1": KOT_PARADIGM},
        {},
        overrides,
    )
    lore = lore_of(sources, "KOT", TextLexicon.from_words(["KOT"]))
    assert [reading.lexeme for reading in lore.readings] == ["wykrzyknik:KOT:"]


def test_an_override_carrying_no_analysis_answers_no_reading() -> None:
    rescue = {
        "ABBOZZO": (
            RescueRow(lemma="abbozzo", tag="subst:sg:nom:n:ncol", name="nazwa_pospolita", label=""),
        )
    }
    sources = _sources({}, {}, rescue, {"ABBOZZO": ()})
    lore = lore_of(sources, "ABBOZZO", TextLexicon.from_words(["ABBOZZO"]))
    assert lore.playable is True
    assert lore.readings == ()


def test_a_homonym_answers_one_reading_for_each_lexeme() -> None:
    sources = _sources(
        {
            "bronią": [
                ("bronią", "broń:Sf", "subst:sg:inst:f", [], []),
                ("bronią", "bronić:V", "fin:pl:ter:imperf", [], []),
            ]
        },
        {},
        {},
    )
    lore = lore_of(sources, "BRONIĄ", TextLexicon.from_words(["BRONIĄ"]))
    assert [reading.lexeme for reading in lore.readings] == [
        "czasownik:BRONIĆ:V",
        "rzeczownik:BROŃ:Sf",
    ]


@requires_morfeusz2
def test_picia_reads_as_a_verbal_noun_and_a_noun_with_no_invented_comparative() -> None:
    sources = LoreSources(engine=build_morfeusz_engine(), rescue={}, overrides={})
    lore = lore_of(sources, "PICIA", TextLexicon.from_words(["PICIA", "PICIE", "PICIU", "PIĆ"]))
    assert {reading.lexeme for reading in lore.readings} == {"czasownik:PIĆ:", "rzeczownik:PICIE:"}
    assert all(reading.part is not PartOfSpeech.PRZYMIOTNIK for reading in lore.readings)
    forms = {form.text for reading in lore.readings for form in reading.forms}
    assert "PICISZY" not in forms


def test_the_morphology_sources_read_the_polish_dictionaries() -> None:
    assert morphology_covers(DictionaryName.SJP) is True
    assert morphology_covers(DictionaryName.OSPS) is True
    assert morphology_covers(DictionaryName.ENGLISH) is False
