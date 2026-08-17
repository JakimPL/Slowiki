import pytest

from lexica.morph.mapping import build_analysis, morph_tags, part_of_speech
from lexica.morph.models import Analysis, MorphSource, MorphTags, class_key
from lexica.morph.parts import PartOfSpeech
from lexica.morph.tags import (
    Aspect,
    Case,
    Degree,
    Gender,
    Mood,
    Number,
    NumeralType,
    Person,
    PronounType,
    Tense,
    VerbForm,
)

PART_CASES = [
    ("subst:sg:nom:m3", PartOfSpeech.RZECZOWNIK),
    ("depr:pl:nom.acc.voc:m2", PartOfSpeech.RZECZOWNIK),
    ("adj:sg:acc:m3:pos", PartOfSpeech.PRZYMIOTNIK),
    ("adjp:dat", PartOfSpeech.PRZYMIOTNIK),
    ("adjc", PartOfSpeech.PRZYMIOTNIK),
    ("adv:com", PartOfSpeech.PRZYSŁÓWEK),
    ("num:pl:nom.acc.voc:m1.n:rec:col", PartOfSpeech.LICZEBNIK),
    ("frag", PartOfSpeech.LICZEBNIK),
    ("ppron12:sg:voc:m1.m2.m3.f.n:sec", PartOfSpeech.ZAIMEK),
    ("ppron3:sg:gen:n:ter:akc:npraep", PartOfSpeech.ZAIMEK),
    ("siebie:acc", PartOfSpeech.ZAIMEK),
    ("prep:loc", PartOfSpeech.PRZYIMEK),
    ("conj", PartOfSpeech.SPÓJNIK),
    ("part", PartOfSpeech.PARTYKUŁA),
    ("comp", PartOfSpeech.PARTYKUŁA),
    ("interj", PartOfSpeech.WYKRZYKNIK),
    ("fin:sg:ter:imperf", PartOfSpeech.CZASOWNIK),
    ("bedzie:sg:ter:imperf", PartOfSpeech.CZASOWNIK),
    ("aglt:sg:pri:imperf:nwok", PartOfSpeech.CZASOWNIK),
    ("praet:sg:m1:imperf", PartOfSpeech.CZASOWNIK),
    ("impt:sg:sec:imperf", PartOfSpeech.CZASOWNIK),
    ("imps:imperf", PartOfSpeech.CZASOWNIK),
    ("inf:imperf", PartOfSpeech.CZASOWNIK),
    ("pcon:imperf", PartOfSpeech.CZASOWNIK),
    ("pant:perf", PartOfSpeech.CZASOWNIK),
    ("pact:sg:nom:m1:imperf:aff", PartOfSpeech.CZASOWNIK),
    ("ppas:sg:nom:m1:perf:aff", PartOfSpeech.CZASOWNIK),
    ("ger:sg:nom:n:imperf:aff", PartOfSpeech.CZASOWNIK),
    ("winien:sg:m1.m2.m3:imperf", PartOfSpeech.CZASOWNIK),
    ("pred", PartOfSpeech.CZASOWNIK),
    ("brev:npun", PartOfSpeech.INNY),
    ("romandig", PartOfSpeech.INNY),
    ("ign", PartOfSpeech.INNY),
    ("xx", PartOfSpeech.INNY),
]

TAG_CASES = [
    (
        "subst:sg:inst:f",
        MorphTags(
            cases=frozenset({Case.NARZĘDNIK}),
            number=Number.POJEDYNCZA,
            genders=frozenset({Gender.ŻEŃSKI}),
        ),
    ),
    (
        "subst:pl:nom.acc.voc:m1",
        MorphTags(
            cases=frozenset({Case.MIANOWNIK, Case.BIERNIK, Case.WOŁACZ}),
            number=Number.MNOGA,
            genders=frozenset({Gender.MĘSKOOSOBOWY}),
        ),
    ),
    (
        "subst:pl:gen:n:ncol",
        MorphTags(
            cases=frozenset({Case.DOPEŁNIACZ}),
            number=Number.MNOGA,
            genders=frozenset({Gender.NIJAKI}),
            extras=frozenset({"ncol"}),
        ),
    ),
    (
        "depr:pl:nom.acc.voc:m2",
        MorphTags(
            cases=frozenset({Case.MIANOWNIK, Case.BIERNIK, Case.WOŁACZ}),
            number=Number.MNOGA,
            genders=frozenset({Gender.MĘSKOZWIERZĘCY}),
            deprecative=True,
        ),
    ),
    (
        "fin:pl:ter:imperf",
        MorphTags(
            number=Number.MNOGA,
            person=Person.TRZECIA,
            aspects=frozenset({Aspect.NIEDOKONANY}),
            tense=Tense.TERAŹNIEJSZY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_OSOBOWA,
        ),
    ),
    (
        "fin:sg:pri:perf",
        MorphTags(
            number=Number.POJEDYNCZA,
            person=Person.PIERWSZA,
            aspects=frozenset({Aspect.DOKONANY}),
            tense=Tense.PRZYSZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_OSOBOWA,
        ),
    ),
    (
        "bedzie:sg:ter:imperf",
        MorphTags(
            number=Number.POJEDYNCZA,
            person=Person.TRZECIA,
            aspects=frozenset({Aspect.NIEDOKONANY}),
            tense=Tense.PRZYSZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_OSOBOWA,
        ),
    ),
    (
        "praet:sg:m1:imperf",
        MorphTags(
            number=Number.POJEDYNCZA,
            genders=frozenset({Gender.MĘSKOOSOBOWY}),
            aspects=frozenset({Aspect.NIEDOKONANY}),
            tense=Tense.PRZESZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_PRZESZŁA,
        ),
    ),
    (
        "praet:sg:f:imperf.perf",
        MorphTags(
            number=Number.POJEDYNCZA,
            genders=frozenset({Gender.ŻEŃSKI}),
            aspects=frozenset({Aspect.NIEDOKONANY, Aspect.DOKONANY}),
            tense=Tense.PRZESZŁY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.FORMA_PRZESZŁA,
        ),
    ),
    (
        "impt:sg:sec:perf",
        MorphTags(
            number=Number.POJEDYNCZA,
            person=Person.DRUGA,
            aspects=frozenset({Aspect.DOKONANY}),
            mood=Mood.ROZKAZUJĄCY,
            verb_form=VerbForm.ROZKAŹNIK,
        ),
    ),
    (
        "aglt:sg:pri:imperf:wok",
        MorphTags(
            number=Number.POJEDYNCZA,
            person=Person.PIERWSZA,
            aspects=frozenset({Aspect.NIEDOKONANY}),
            mood=Mood.PRZYPUSZCZAJĄCY,
            verb_form=VerbForm.KOŃCÓWKA_RUCHOMA,
            extras=frozenset({"wok"}),
        ),
    ),
    (
        "ger:pl:gen:n:imperf.perf:neg",
        MorphTags(
            cases=frozenset({Case.DOPEŁNIACZ}),
            number=Number.MNOGA,
            genders=frozenset({Gender.NIJAKI}),
            aspects=frozenset({Aspect.NIEDOKONANY, Aspect.DOKONANY}),
            negation=True,
            verb_form=VerbForm.ODSŁOWNIK,
        ),
    ),
    (
        "pact:pl:nom.voc:m1:imperf:neg",
        MorphTags(
            cases=frozenset({Case.MIANOWNIK, Case.WOŁACZ}),
            number=Number.MNOGA,
            genders=frozenset({Gender.MĘSKOOSOBOWY}),
            aspects=frozenset({Aspect.NIEDOKONANY}),
            negation=True,
            verb_form=VerbForm.IMIESŁÓW_CZYNNY,
        ),
    ),
    (
        "ppas:sg:nom:n:perf:aff",
        MorphTags(
            cases=frozenset({Case.MIANOWNIK}),
            number=Number.POJEDYNCZA,
            genders=frozenset({Gender.NIJAKI}),
            aspects=frozenset({Aspect.DOKONANY}),
            negation=False,
            verb_form=VerbForm.IMIESŁÓW_BIERNY,
        ),
    ),
    (
        "adj:pl:inst:m1.m2.m3.f.n:com",
        MorphTags(
            cases=frozenset({Case.NARZĘDNIK}),
            number=Number.MNOGA,
            genders=frozenset(
                {
                    Gender.MĘSKOOSOBOWY,
                    Gender.MĘSKOZWIERZĘCY,
                    Gender.MĘSKORZECZOWY,
                    Gender.ŻEŃSKI,
                    Gender.NIJAKI,
                }
            ),
            degree=Degree.WYŻSZY,
        ),
    ),
    (
        "adv:sup",
        MorphTags(degree=Degree.NAJWYŻSZY),
    ),
    (
        "num:pl:nom.acc.voc:m1.n:rec:col",
        MorphTags(
            cases=frozenset({Case.MIANOWNIK, Case.BIERNIK, Case.WOŁACZ}),
            number=Number.MNOGA,
            genders=frozenset({Gender.MĘSKOOSOBOWY, Gender.NIJAKI}),
            numeral_type=NumeralType.ZBIOROWY,
            extras=frozenset({"rec", "col"}),
        ),
    ),
    (
        "num:pl:acc:m1:rec",
        MorphTags(
            cases=frozenset({Case.BIERNIK}),
            number=Number.MNOGA,
            genders=frozenset({Gender.MĘSKOOSOBOWY}),
            numeral_type=NumeralType.GŁÓWNY,
            extras=frozenset({"rec"}),
        ),
    ),
    (
        "frag",
        MorphTags(),
    ),
    (
        "ppron3:sg:gen:n:ter:akc:npraep",
        MorphTags(
            cases=frozenset({Case.DOPEŁNIACZ}),
            number=Number.POJEDYNCZA,
            genders=frozenset({Gender.NIJAKI}),
            person=Person.TRZECIA,
            pronoun_type=PronounType.OSOBOWY,
            extras=frozenset({"akc", "npraep"}),
        ),
    ),
    (
        "siebie:acc",
        MorphTags(
            cases=frozenset({Case.BIERNIK}),
            pronoun_type=PronounType.ZWROTNY,
        ),
    ),
    (
        "prep:acc:nwok",
        MorphTags(
            cases=frozenset({Case.BIERNIK}),
            extras=frozenset({"nwok"}),
        ),
    ),
    (
        "winien:sg:m1.m2.m3:imperf",
        MorphTags(
            number=Number.POJEDYNCZA,
            genders=frozenset({Gender.MĘSKOOSOBOWY, Gender.MĘSKOZWIERZĘCY, Gender.MĘSKORZECZOWY}),
            aspects=frozenset({Aspect.NIEDOKONANY}),
            tense=Tense.TERAŹNIEJSZY,
            mood=Mood.OZNAJMUJĄCY,
            verb_form=VerbForm.WINIEN,
        ),
    ),
    (
        "pred",
        MorphTags(verb_form=VerbForm.PREDYKATYW),
    ),
    (
        "brev:npun",
        MorphTags(extras=frozenset({"npun"})),
    ),
]


@pytest.mark.parametrize(("tag", "part"), PART_CASES)
def test_part_of_speech(tag: str, part: PartOfSpeech) -> None:
    assert part_of_speech(tag) is part


@pytest.mark.parametrize(("tag", "expected"), TAG_CASES)
def test_morph_tags(tag: str, expected: MorphTags) -> None:
    assert morph_tags(tag) == expected


def test_bronia_belongs_to_two_classes() -> None:
    noun = build_analysis(
        "bronią", "broń", "subst:sg:inst:f", MorphSource.SGJP, ("nazwa_pospolita",)
    )
    assert noun.part is PartOfSpeech.RZECZOWNIK
    assert noun.lemma == "broń"
    assert noun.tags.cases == frozenset({Case.NARZĘDNIK})
    assert noun.tags.number is Number.POJEDYNCZA

    verb = build_analysis("bronią", "bronić", "fin:pl:ter:imperf", MorphSource.SGJP, ())
    assert verb.part is PartOfSpeech.CZASOWNIK
    assert verb.lemma == "bronić"
    assert verb.tags.verb_form is VerbForm.FORMA_OSOBOWA
    assert verb.tags.person is Person.TRZECIA
    assert verb.tags.tense is Tense.TERAŹNIEJSZY


def test_zamek_homonyms_keep_separate_lemmas() -> None:
    castle = build_analysis("zamek", "zamek:Sm3~u", "subst:sg:nom.acc:m3", MorphSource.SGJP, ())
    zipper = build_analysis("zamek", "zamek:Sm3~a", "subst:sg:nom.acc:m3", MorphSource.SGJP, ())
    assert castle.lemma == "zamek:Sm3~u"
    assert zipper.lemma == "zamek:Sm3~a"
    assert class_key(castle.lemma, PartOfSpeech.RZECZOWNIK) != class_key(
        zipper.lemma, PartOfSpeech.RZECZOWNIK
    )


def test_class_key_shape() -> None:
    assert class_key("kot:Sm1", PartOfSpeech.RZECZOWNIK) == "rzeczownik:kot:Sm1"


def test_build_analysis_returns_complete_model() -> None:
    analysis = build_analysis("kotem", "kot:Sm1", "subst:sg:inst:m1", MorphSource.SGJP, ())
    assert analysis == Analysis(
        surface="kotem",
        lemma="kot:Sm1",
        tag="subst:sg:inst:m1",
        part=PartOfSpeech.RZECZOWNIK,
        tags=MorphTags(
            cases=frozenset({Case.NARZĘDNIK}),
            number=Number.POJEDYNCZA,
            genders=frozenset({Gender.MĘSKOOSOBOWY}),
        ),
        source=MorphSource.SGJP,
    )
