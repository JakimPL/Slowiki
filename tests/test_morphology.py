import pytest

from lexica.build.orchestrate import analyse_dictionary
from lexica.lore.lexeme_id import token_of
from lexica.sources.sgjp import analyse_word, build_morfeusz_engine, generate_paradigm

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
def test_picia_reads_as_the_verbal_noun_of_pic_and_the_noun_picie() -> None:
    engine = build_morfeusz_engine()
    result = analyse_dictionary(("PICIA", "PICIE", "PICIU", "PICIEM"), engine, None)
    tokens = {token_of(lexeme) for lexeme in result.store.entries["PICIA"]}
    assert tokens == {"czasownik:PIĆ:", "rzeczownik:PICIE:"}

    picie = next(lexeme for lexeme in result.store.entries["PICIA"] if lexeme.lemma == "PICIE")
    record = result.store.classes[picie]
    assert record.base == "PICIE"
    forms = {variant.form for variant in record.variants}
    assert {"PICIE", "PICIA", "PICIU", "PICIEM", "PICIACH"} <= forms
    assert not any(form.endswith("SZY") for form in forms)


@requires_morfeusz2
def test_a_generated_form_outside_the_dictionary_is_marked() -> None:
    engine = build_morfeusz_engine()
    result = analyse_dictionary(("ZAMEK", "ZAMKA"), engine, None)
    hard = next(lexeme for lexeme in result.store.entries["ZAMEK"] if lexeme.pattern == "Sm3~a")
    membership = {
        variant.form: variant.in_dictionary for variant in result.store.classes[hard].variants
    }
    assert membership["ZAMEK"] is True
    assert membership["ZAMKA"] is True
    assert membership["ZAMKOWI"] is False
