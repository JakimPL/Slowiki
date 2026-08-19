from collections.abc import Iterable
from typing import TypeVar

import pytest
from tests.fixtures.inflections import an_inflection

from lexica.grammar.aspect import Aspect
from lexica.grammar.case import Case
from lexica.grammar.degree import Degree
from lexica.grammar.dialect import TagsetDialect
from lexica.grammar.gender import Gender
from lexica.grammar.inflection import Inflection
from lexica.grammar.mood import Mood
from lexica.grammar.number import Number
from lexica.grammar.numeral_type import NumeralType
from lexica.grammar.parse import inflection_of, part_of_speech
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.grammar.person import Person
from lexica.grammar.pronoun_type import PronounType
from lexica.grammar.quality import Quality
from lexica.grammar.segments import SegmentTable
from lexica.grammar.tables import segment_table
from lexica.grammar.tense import Tense
from lexica.grammar.verb_form import VerbForm
from wordcore.errors.exceptions import InvalidConfiguration

MASCULINE = (Gender.MĘSKOOSOBOWY, Gender.MĘSKOZWIERZĘCY, Gender.MĘSKORZECZOWY)
EVERY_GENDER = (*MASCULINE, Gender.ŻEŃSKI, Gender.NIJAKI)

SGJP_PART_CASES = [
    ("subst:sg:nom:m3", PartOfSpeech.RZECZOWNIK),
    ("depr:pl:nom.acc.voc:m2", PartOfSpeech.RZECZOWNIK),
    ("adj:sg:acc:m3:pos", PartOfSpeech.PRZYMIOTNIK),
    ("adja", PartOfSpeech.PRZYMIOTNIK),
    ("adjc", PartOfSpeech.PRZYMIOTNIK),
    ("adjp:dat", PartOfSpeech.PRZYMIOTNIK),
    ("adv:com", PartOfSpeech.PRZYSŁÓWEK),
    ("num:pl:nom.acc.voc:m1.n:rec:col", PartOfSpeech.LICZEBNIK),
    ("numcomp", PartOfSpeech.LICZEBNIK),
    ("frag", PartOfSpeech.LICZEBNIK),
    ("ppron12:sg:voc:m1.m2.m3.f.n:sec", PartOfSpeech.ZAIMEK),
    ("ppron3:sg:gen:n:ter:akc:npraep", PartOfSpeech.ZAIMEK),
    ("siebie:acc", PartOfSpeech.ZAIMEK),
    ("prep:loc", PartOfSpeech.PRZYIMEK),
    ("conj", PartOfSpeech.SPÓJNIK),
    ("comp", PartOfSpeech.SPÓJNIK),
    ("part", PartOfSpeech.PARTYKUŁA),
    ("qub", PartOfSpeech.PARTYKUŁA),
    ("interj", PartOfSpeech.WYKRZYKNIK),
    ("fin:sg:ter:imperf", PartOfSpeech.CZASOWNIK),
    ("bedzie:sg:ter:imperf", PartOfSpeech.CZASOWNIK),
    ("aglt:sg:pri:imperf:nwok", PartOfSpeech.CZASOWNIK),
    ("praet:sg:m1:imperf", PartOfSpeech.CZASOWNIK),
    ("cond:sg:m1.m2.m3:pri:perf", PartOfSpeech.CZASOWNIK),
    ("impt:sg:sec:imperf", PartOfSpeech.CZASOWNIK),
    ("imps:imperf", PartOfSpeech.CZASOWNIK),
    ("inf:imperf", PartOfSpeech.CZASOWNIK),
    ("pcon:imperf", PartOfSpeech.CZASOWNIK),
    ("pant:perf", PartOfSpeech.CZASOWNIK),
    ("pact:sg:nom:m1:imperf:aff", PartOfSpeech.CZASOWNIK),
    ("pacta", PartOfSpeech.CZASOWNIK),
    ("ppas:sg:nom:m1:perf:aff", PartOfSpeech.CZASOWNIK),
    ("ger:sg:nom:n:imperf:aff", PartOfSpeech.CZASOWNIK),
    ("winien:sg:m1.m2.m3:imperf", PartOfSpeech.CZASOWNIK),
    ("pred", PartOfSpeech.CZASOWNIK),
    ("brev:npun", PartOfSpeech.INNY),
    ("romandig", PartOfSpeech.INNY),
    ("ign", PartOfSpeech.INNY),
    ("xx", PartOfSpeech.INNY),
]

POLIMORF_PART_CASES = [
    ("burk", PartOfSpeech.INNY),
    ("comp", PartOfSpeech.SPÓJNIK),
    ("qub", PartOfSpeech.PARTYKUŁA),
    ("num:comp", PartOfSpeech.LICZEBNIK),
    ("subst:sg:gen:n2", PartOfSpeech.RZECZOWNIK),
]

SGJP_TAG_CASES = [
    (
        "subst:sg:inst:f",
        an_inflection(
            cases=[Case.NARZĘDNIK],
            numbers=[Number.POJEDYNCZA],
            genders=[Gender.ŻEŃSKI],
        ),
    ),
    (
        "subst:pl:nom.acc.voc:m1",
        an_inflection(
            cases=[Case.MIANOWNIK, Case.BIERNIK, Case.WOŁACZ],
            numbers=[Number.MNOGA],
            genders=[Gender.MĘSKOOSOBOWY],
        ),
    ),
    (
        "subst:pl:gen:n:ncol",
        an_inflection(
            cases=[Case.DOPEŁNIACZ],
            numbers=[Number.MNOGA],
            genders=[Gender.NIJAKI],
            qualities=[Quality.NIEZBIOROWY],
        ),
    ),
    (
        "subst:sg.pl:nom.gen.dat.acc.inst.loc.voc:n:ncol",
        an_inflection(
            cases=list(Case),
            numbers=[Number.POJEDYNCZA, Number.MNOGA],
            genders=[Gender.NIJAKI],
            qualities=[Quality.NIEZBIOROWY],
        ),
    ),
    (
        "subst:pl:nom.voc:n:pt",
        an_inflection(
            cases=[Case.MIANOWNIK, Case.WOŁACZ],
            numbers=[Number.MNOGA],
            genders=[Gender.NIJAKI],
            qualities=[Quality.PLURALE_TANTUM],
        ),
    ),
    (
        "depr:pl:nom.acc.voc:m2",
        an_inflection(
            cases=[Case.MIANOWNIK, Case.BIERNIK, Case.WOŁACZ],
            numbers=[Number.MNOGA],
            genders=[Gender.MĘSKOZWIERZĘCY],
            deprecative=True,
        ),
    ),
    (
        "fin:pl:ter:imperf",
        an_inflection(
            numbers=[Number.MNOGA],
            person=Person.TRZECIA,
            aspects=[Aspect.NIEDOKONANY],
            tense=Tense.TERAŹNIEJSZY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_OSOBOWA,
        ),
    ),
    (
        "fin:sg:pri:perf",
        an_inflection(
            numbers=[Number.POJEDYNCZA],
            person=Person.PIERWSZA,
            aspects=[Aspect.DOKONANY],
            tense=Tense.PRZYSZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_OSOBOWA,
        ),
    ),
    (
        "bedzie:sg:ter:imperf",
        an_inflection(
            numbers=[Number.POJEDYNCZA],
            person=Person.TRZECIA,
            aspects=[Aspect.NIEDOKONANY],
            tense=Tense.PRZYSZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_OSOBOWA,
        ),
    ),
    (
        "praet:sg:m1:imperf",
        an_inflection(
            numbers=[Number.POJEDYNCZA],
            genders=[Gender.MĘSKOOSOBOWY],
            aspects=[Aspect.NIEDOKONANY],
            tense=Tense.PRZESZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_PRZESZŁA,
        ),
    ),
    (
        "praet:sg:f:imperf.perf",
        an_inflection(
            numbers=[Number.POJEDYNCZA],
            genders=[Gender.ŻEŃSKI],
            aspects=[Aspect.NIEDOKONANY, Aspect.DOKONANY],
            tense=Tense.PRZESZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_PRZESZŁA,
        ),
    ),
    (
        "praet:sg:m1.m2.m3:pri:imperf",
        an_inflection(
            numbers=[Number.POJEDYNCZA],
            genders=MASCULINE,
            person=Person.PIERWSZA,
            aspects=[Aspect.NIEDOKONANY],
            tense=Tense.PRZESZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_PRZESZŁA,
        ),
    ),
    (
        "praet:sg:m1.m2.m3:imperf:nagl",
        an_inflection(
            numbers=[Number.POJEDYNCZA],
            genders=MASCULINE,
            aspects=[Aspect.NIEDOKONANY],
            tense=Tense.PRZESZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_PRZESZŁA,
            qualities=[Quality.NIEAGLUTYNACYJNY],
        ),
    ),
    (
        "cond:pl:m2.m3.f.n:ter:imperf.perf",
        an_inflection(
            numbers=[Number.MNOGA],
            genders=[
                Gender.MĘSKOZWIERZĘCY,
                Gender.MĘSKORZECZOWY,
                Gender.ŻEŃSKI,
                Gender.NIJAKI,
            ],
            person=Person.TRZECIA,
            aspects=[Aspect.NIEDOKONANY, Aspect.DOKONANY],
            mood=Mood.PRZYPUSZCZAJĄCY,
            verb_form=VerbForm.FORMA_PRZYPUSZCZAJĄCA,
        ),
    ),
    (
        "impt:sg:sec:perf",
        an_inflection(
            numbers=[Number.POJEDYNCZA],
            person=Person.DRUGA,
            aspects=[Aspect.DOKONANY],
            mood=Mood.ROZKAZUJĄCY,
            verb_form=VerbForm.ROZKAŹNIK,
        ),
    ),
    (
        "aglt:sg:pri:imperf:wok",
        an_inflection(
            numbers=[Number.POJEDYNCZA],
            person=Person.PIERWSZA,
            aspects=[Aspect.NIEDOKONANY],
            verb_form=VerbForm.KOŃCÓWKA_RUCHOMA,
            qualities=[Quality.WOKALICZNY],
        ),
    ),
    (
        "imps:imperf",
        an_inflection(
            aspects=[Aspect.NIEDOKONANY],
            verb_form=VerbForm.BEZOSOBNIK,
        ),
    ),
    (
        "inf:perf",
        an_inflection(aspects=[Aspect.DOKONANY], verb_form=VerbForm.BEZOKOLICZNIK),
    ),
    (
        "pcon:imperf",
        an_inflection(
            aspects=[Aspect.NIEDOKONANY],
            verb_form=VerbForm.IMIESŁÓW_WSPÓŁCZESNY,
        ),
    ),
    (
        "pant:perf",
        an_inflection(aspects=[Aspect.DOKONANY], verb_form=VerbForm.IMIESŁÓW_UPRZEDNI),
    ),
    (
        "ger:pl:gen:n:imperf.perf:neg",
        an_inflection(
            cases=[Case.DOPEŁNIACZ],
            numbers=[Number.MNOGA],
            genders=[Gender.NIJAKI],
            aspects=[Aspect.NIEDOKONANY, Aspect.DOKONANY],
            negation=True,
            verb_form=VerbForm.ODSŁOWNIK,
        ),
    ),
    (
        "pact:pl:nom.voc:m1:imperf:neg",
        an_inflection(
            cases=[Case.MIANOWNIK, Case.WOŁACZ],
            numbers=[Number.MNOGA],
            genders=[Gender.MĘSKOOSOBOWY],
            aspects=[Aspect.NIEDOKONANY],
            negation=True,
            verb_form=VerbForm.IMIESŁÓW_CZYNNY,
        ),
    ),
    ("pacta", an_inflection(verb_form=VerbForm.IMIESŁÓW_CZYNNY)),
    (
        "ppas:sg:nom:n:perf:aff",
        an_inflection(
            cases=[Case.MIANOWNIK],
            numbers=[Number.POJEDYNCZA],
            genders=[Gender.NIJAKI],
            aspects=[Aspect.DOKONANY],
            negation=False,
            verb_form=VerbForm.IMIESŁÓW_BIERNY,
        ),
    ),
    (
        "adj:pl:inst:m1.m2.m3.f.n:com",
        an_inflection(
            cases=[Case.NARZĘDNIK],
            numbers=[Number.MNOGA],
            genders=EVERY_GENDER,
            degree=Degree.WYŻSZY,
        ),
    ),
    ("adv:sup", an_inflection(degree=Degree.NAJWYŻSZY)),
    ("adja", an_inflection(qualities=[Quality.ZŁOŻONY])),
    (
        "adjp:dat",
        an_inflection(cases=[Case.CELOWNIK], qualities=[Quality.POPRZYIMKOWY]),
    ),
    (
        "num:pl:nom.acc.voc:m1.n:rec:col",
        an_inflection(
            cases=[Case.MIANOWNIK, Case.BIERNIK, Case.WOŁACZ],
            numbers=[Number.MNOGA],
            genders=[Gender.MĘSKOOSOBOWY, Gender.NIJAKI],
            numeral_type=NumeralType.ZBIOROWY,
            qualities=[Quality.RZĄDZĄCY, Quality.ZBIOROWY],
        ),
    ),
    (
        "num:pl:acc:m1:congr",
        an_inflection(
            cases=[Case.BIERNIK],
            numbers=[Number.MNOGA],
            genders=[Gender.MĘSKOOSOBOWY],
            numeral_type=NumeralType.GŁÓWNY,
            qualities=[Quality.UZGADNIAJĄCY],
        ),
    ),
    ("numcomp", an_inflection(qualities=[Quality.ZŁOŻONY])),
    ("frag", an_inflection()),
    (
        "ppron12:sg:voc:m1.m2.m3.f.n:sec:akc.nakc",
        an_inflection(
            cases=[Case.WOŁACZ],
            numbers=[Number.POJEDYNCZA],
            genders=EVERY_GENDER,
            person=Person.DRUGA,
            pronoun_type=PronounType.OSOBOWY,
            qualities=[Quality.AKCENTOWANY, Quality.NIEAKCENTOWANY],
        ),
    ),
    (
        "ppron3:sg:gen:n:ter:akc:npraep",
        an_inflection(
            cases=[Case.DOPEŁNIACZ],
            numbers=[Number.POJEDYNCZA],
            genders=[Gender.NIJAKI],
            person=Person.TRZECIA,
            pronoun_type=PronounType.OSOBOWY,
            qualities=[Quality.AKCENTOWANY, Quality.NIEPOPRZYIMKOWY],
        ),
    ),
    (
        "siebie:acc",
        an_inflection(cases=[Case.BIERNIK], pronoun_type=PronounType.ZWROTNY),
    ),
    (
        "winien:sg:m1.m2.m3:imperf",
        an_inflection(
            numbers=[Number.POJEDYNCZA],
            genders=MASCULINE,
            aspects=[Aspect.NIEDOKONANY],
            tense=Tense.TERAŹNIEJSZY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.WINIEN,
        ),
    ),
    ("pred", an_inflection(verb_form=VerbForm.PREDYKATYW)),
    ("brev:npun", an_inflection(qualities=[Quality.NIEKROPKOWANY])),
    ("brev:pun", an_inflection(qualities=[Quality.KROPKOWANY])),
]

REKCJA_CASES = [
    ("prep:gen", an_inflection(governed_case=Case.DOPEŁNIACZ)),
    (
        "prep:acc:nwok",
        an_inflection(governed_case=Case.BIERNIK, qualities=[Quality.NIEWOKALICZNY]),
    ),
    (
        "prep:inst:wok",
        an_inflection(governed_case=Case.NARZĘDNIK, qualities=[Quality.WOKALICZNY]),
    ),
    ("prep:nom", an_inflection(governed_case=Case.MIANOWNIK)),
]

POLIMORF_TAG_CASES = [
    (
        "subst:sg:gen:n2",
        an_inflection(
            cases=[Case.DOPEŁNIACZ],
            numbers=[Number.POJEDYNCZA],
            genders=[Gender.NIJAKI],
        ),
    ),
    (
        "subst:pl:nom:p3",
        an_inflection(
            cases=[Case.MIANOWNIK],
            numbers=[Number.MNOGA],
            genders=[Gender.NIJAKI],
        ),
    ),
    (
        "adj:pl:nom.voc:m1.p1:pos",
        an_inflection(
            cases=[Case.MIANOWNIK, Case.WOŁACZ],
            numbers=[Number.MNOGA],
            genders=[Gender.MĘSKOOSOBOWY],
            degree=Degree.RÓWNY,
        ),
    ),
    (
        "adj:pl:gen:m1.m2.m3.f.n1.n2.p1.p2.p3:pos",
        an_inflection(
            cases=[Case.DOPEŁNIACZ],
            numbers=[Number.MNOGA],
            genders=EVERY_GENDER,
            degree=Degree.RÓWNY,
        ),
    ),
    (
        "ppron12:pl:acc:_:pri",
        an_inflection(
            cases=[Case.BIERNIK],
            numbers=[Number.MNOGA],
            person=Person.PIERWSZA,
            pronoun_type=PronounType.OSOBOWY,
        ),
    ),
    (
        "num:comp",
        an_inflection(numeral_type=NumeralType.GŁÓWNY, qualities=[Quality.ZŁOŻONY]),
    ),
    ("burk", an_inflection()),
]

SHARED_TAGS = [
    "subst:sg:inst:f",
    "subst:pl:nom.acc.voc:m1",
    "depr:pl:nom.acc.voc:m2",
    "adj:sg:nom:m3:pos",
    "adv:com",
    "fin:pl:ter:imperf",
    "praet:sg:f:imperf",
    "impt:sg:sec:perf",
    "aglt:sg:pri:imperf:wok",
    "pact:pl:nom.voc:m1:imperf:neg",
    "prep:acc:nwok",
    "winien:sg:m1.m2.m3:imperf",
    "pred",
]

SGJP_ONLY_TAGS = ["cond:sg:f:pri:perf", "siebie:acc", "frag", "brev:npun", "subst:pl:gen:n:ncol"]

POLIMORF_ONLY_TAGS = ["burk", "subst:sg:gen:n2", "subst:pl:nom:p1", "ppron12:pl:acc:_:pri"]

MALFORMED_TAGS = [
    "subst:sg:zzz:m1",
    "zzz:sg",
    "fin:sg:pri.sec:imperf",
    "adj:sg:nom:m3:pos.com",
    "prep:gen.acc",
]

_NEGATIONS = ("aff", "neg")

_Value = TypeVar("_Value")


@pytest.mark.parametrize(("tag", "part"), SGJP_PART_CASES)
def test_the_sgjp_tagset_names_a_part_of_speech(tag: str, part: PartOfSpeech) -> None:
    assert part_of_speech(tag, TagsetDialect.SGJP) is part


@pytest.mark.parametrize(("tag", "part"), POLIMORF_PART_CASES)
def test_the_polimorf_tagset_names_a_part_of_speech(tag: str, part: PartOfSpeech) -> None:
    assert part_of_speech(tag, TagsetDialect.POLIMORF) is part


@pytest.mark.parametrize(("tag", "expected"), SGJP_TAG_CASES)
def test_an_sgjp_tag_digests_into_an_inflection(tag: str, expected: Inflection) -> None:
    assert inflection_of(tag, TagsetDialect.SGJP) == expected


@pytest.mark.parametrize(("tag", "expected"), REKCJA_CASES)
def test_a_preposition_states_the_case_it_governs(tag: str, expected: Inflection) -> None:
    inflection = inflection_of(tag, TagsetDialect.SGJP)
    assert inflection == expected
    assert inflection.cases == frozenset()


@pytest.mark.parametrize(("tag", "expected"), POLIMORF_TAG_CASES)
def test_a_polimorf_tag_digests_into_an_inflection(tag: str, expected: Inflection) -> None:
    assert inflection_of(tag, TagsetDialect.POLIMORF) == expected


@pytest.mark.parametrize("tag", SHARED_TAGS)
def test_a_shared_tag_reads_the_same_in_both_dialects(tag: str) -> None:
    assert inflection_of(tag, TagsetDialect.SGJP) == inflection_of(tag, TagsetDialect.POLIMORF)
    assert part_of_speech(tag, TagsetDialect.SGJP) is part_of_speech(tag, TagsetDialect.POLIMORF)


@pytest.mark.parametrize("tag", SGJP_ONLY_TAGS)
def test_the_polimorf_tagset_refuses_an_sgjp_tag(tag: str) -> None:
    inflection_of(tag, TagsetDialect.SGJP)
    with pytest.raises(InvalidConfiguration):
        inflection_of(tag, TagsetDialect.POLIMORF)


@pytest.mark.parametrize("tag", POLIMORF_ONLY_TAGS)
def test_the_sgjp_tagset_refuses_a_polimorf_tag(tag: str) -> None:
    inflection_of(tag, TagsetDialect.POLIMORF)
    with pytest.raises(InvalidConfiguration):
        inflection_of(tag, TagsetDialect.SGJP)


@pytest.mark.parametrize("tag", MALFORMED_TAGS)
def test_a_tag_outside_the_tagset_is_refused(tag: str) -> None:
    with pytest.raises(InvalidConfiguration):
        inflection_of(tag, TagsetDialect.SGJP)


def test_a_refusal_names_the_dialect_and_the_tag() -> None:
    with pytest.raises(InvalidConfiguration) as refusal:
        inflection_of("subst:sg:zzz:m1", TagsetDialect.SGJP)
    assert "sgjp" in str(refusal.value)
    assert "zzz" in str(refusal.value)
    assert "subst:sg:zzz:m1" in str(refusal.value)


def test_the_movable_ending_states_no_mood() -> None:
    assert inflection_of("aglt:sg:pri:imperf:wok", TagsetDialect.SGJP).mood is None


def test_the_conditional_states_its_mood_and_its_person() -> None:
    inflection = inflection_of("cond:sg:m1.m2.m3:pri:perf", TagsetDialect.SGJP)
    assert inflection.mood is Mood.PRZYPUSZCZAJĄCY
    assert inflection.verb_form is VerbForm.FORMA_PRZYPUSZCZAJĄCA
    assert inflection.person is Person.PIERWSZA
    assert inflection.tense is None


def test_an_indeclinable_noun_states_both_numbers() -> None:
    inflection = inflection_of("subst:sg.pl:nom:n:ncol", TagsetDialect.SGJP)
    assert inflection.numbers == frozenset({Number.POJEDYNCZA, Number.MNOGA})


@pytest.mark.parametrize("dialect", list(TagsetDialect))
def test_every_grammar_member_is_reachable(dialect: TagsetDialect) -> None:
    inflections = [inflection_of(tag, dialect) for tag in _every_tag(dialect)]
    parts = {part_of_speech(tag, dialect) for tag in _every_tag(dialect)}
    table = segment_table(dialect)

    assert parts == set(table.parts.values())
    assert _united(inflection.cases for inflection in inflections) == set(table.cases.values())
    assert _united(inflection.numbers for inflection in inflections) == set(table.numbers.values())
    assert _united(inflection.genders for inflection in inflections) == {
        gender for genders in table.genders.values() for gender in genders
    }
    assert _united(inflection.aspects for inflection in inflections) == set(table.aspects.values())
    assert _united(inflection.qualities for inflection in inflections) >= set(
        table.qualities.values()
    )
    assert _stated(inflection.governed_case for inflection in inflections) == set(
        table.cases.values()
    )
    assert _stated(inflection.person for inflection in inflections) == set(table.persons.values())
    assert _stated(inflection.degree for inflection in inflections) == set(table.degrees.values())
    assert _stated(inflection.negation for inflection in inflections) == {True, False}


def test_the_whole_grammar_vocabulary_is_produced() -> None:
    inflections = [
        inflection_of(tag, dialect) for dialect in TagsetDialect for tag in _every_tag(dialect)
    ]
    parts = {
        part_of_speech(tag, dialect) for dialect in TagsetDialect for tag in _every_tag(dialect)
    }

    assert parts == set(PartOfSpeech)
    assert _united(inflection.cases for inflection in inflections) == set(Case)
    assert _united(inflection.numbers for inflection in inflections) == set(Number)
    assert _united(inflection.genders for inflection in inflections) == set(Gender)
    assert _united(inflection.aspects for inflection in inflections) == set(Aspect)
    assert _united(inflection.qualities for inflection in inflections) == set(Quality)
    assert _stated(inflection.person for inflection in inflections) == set(Person)
    assert _stated(inflection.tense for inflection in inflections) == set(Tense)
    assert _stated(inflection.mood for inflection in inflections) == set(Mood)
    assert _stated(inflection.degree for inflection in inflections) == set(Degree)
    assert _stated(inflection.verb_form for inflection in inflections) == set(VerbForm)
    assert _stated(inflection.numeral_type for inflection in inflections) == set(NumeralType)
    assert _stated(inflection.pronoun_type for inflection in inflections) == set(PronounType)
    assert {inflection.deprecative for inflection in inflections} == {True, False}


def _every_tag(dialect: TagsetDialect) -> list[str]:
    table = segment_table(dialect)
    codes = _every_code(table)
    return [
        *table.parts,
        *(f"{prefix}:{code}" for prefix in table.parts for code in codes),
        *(f"num:{quality}" for quality in table.qualities),
    ]


def _every_code(table: SegmentTable) -> list[str]:
    return [
        *table.cases,
        *table.numbers,
        *table.genders,
        *table.persons,
        *table.aspects,
        *table.degrees,
        *table.qualities,
        *_NEGATIONS,
    ]


def _united(sets: Iterable[Iterable[_Value]]) -> set[_Value]:
    collected: set[_Value] = set()
    for values in sets:
        collected.update(values)
    return collected


def _stated(values: Iterable[_Value | None]) -> set[_Value]:
    return {value for value in values if value is not None}
