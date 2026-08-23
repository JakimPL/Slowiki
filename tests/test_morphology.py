import pytest

from lexica.lore.lookup import lore_of
from lexica.lore.sources import LoreSources
from lexica.sources.sgjp import analyse_word, build_morfeusz_engine, generate_paradigm
from wordcore.lexicon.lexicon import TextLexicon

try:
    import morfeusz2  # type: ignore[import-untyped]
except ImportError:
    morfeusz2 = None

requires_morfeusz2 = pytest.mark.skipif(morfeusz2 is None, reason="morfeusz2 missing")


@requires_morfeusz2
def test_the_engine_reads_the_person_of_a_past_form() -> None:
    engine = build_morfeusz_engine()
    readings = [
        (analysis.lexeme.lemma, analysis.tag) for analysis in analyse_word(engine, "biegłem")
    ]
    assert readings == [("BIEC", "praet:sg:m1.m2.m3:pri:imperf")]


@requires_morfeusz2
def test_the_engine_reads_a_conditional_as_one_word() -> None:
    engine = build_morfeusz_engine()
    readings = [
        (analysis.lexeme.lemma, analysis.tag) for analysis in analyse_word(engine, "zrobiłbym")
    ]
    assert readings == [("ZROBIĆ", "cond:sg:m1.m2.m3:pri:perf")]


@requires_morfeusz2
def test_each_zamek_homonym_generates_its_own_genitive() -> None:
    engine = build_morfeusz_engine()
    hard = set(generate_paradigm(engine, "zamek:Sm3~a"))
    soft = set(generate_paradigm(engine, "zamek:Sm3~u"))
    assert ("ZAMKA", "subst:sg:gen:m3") in hard
    assert ("ZAMKU", "subst:sg:gen:m3") in soft
    assert ("ZAMKU", "subst:sg:gen:m3") not in hard
    assert ("ZAMKA", "subst:sg:gen:m3") not in soft


@requires_morfeusz2
def test_the_conditional_reaches_the_generated_verb_paradigm() -> None:
    engine = build_morfeusz_engine()
    forms = dict(generate_paradigm(engine, "pić"))
    assert forms["PILIBYŚMY"] == "cond:pl:m1:pri:imperf"
    assert forms["PILIŚMY"] == "praet:pl:m1:pri:imperf"


@requires_morfeusz2
def test_the_odslownik_of_pic_carries_its_whole_case_and_number_grid() -> None:
    sources = LoreSources(engine=build_morfeusz_engine(), rescue={}, overrides={})
    lexicon = TextLexicon.from_words(["PICIA", "PICIE", "PICIU", "PICIEM"])
    picie = next(
        reading
        for reading in lore_of(sources, "PICIA", lexicon).readings
        if reading.lexeme == "rzeczownik:PICIE:"
    )
    assert picie.base == "PICIE"
    forms = {form.text for form in picie.forms}
    assert {"PICIE", "PICIA", "PICIU", "PICIEM", "PICIACH"} <= forms


@requires_morfeusz2
def test_a_generated_form_outside_the_dictionary_is_marked() -> None:
    sources = LoreSources(engine=build_morfeusz_engine(), rescue={}, overrides={})
    lexicon = TextLexicon.from_words(["ZAMEK", "ZAMKA"])
    hard = next(
        reading
        for reading in lore_of(sources, "ZAMEK", lexicon).readings
        if reading.lexeme == "rzeczownik:ZAMEK:Sm3~a"
    )
    membership = {form.text: form.playable for form in hard.forms}
    assert membership["ZAMEK"] is True
    assert membership["ZAMKA"] is True
    assert membership["ZAMKOWI"] is False
