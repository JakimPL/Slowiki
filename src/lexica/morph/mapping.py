from enum import StrEnum
from typing import Final, TypeVar

from lexica.morph.models import Analysis, MorphSource, MorphTags
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

MAPPING_VERSION: Final = 1

_TAG_TO_PART: Final[dict[str, PartOfSpeech]] = {
    "subst": PartOfSpeech.RZECZOWNIK,
    "depr": PartOfSpeech.RZECZOWNIK,
    "adj": PartOfSpeech.PRZYMIOTNIK,
    "adjp": PartOfSpeech.PRZYMIOTNIK,
    "adjc": PartOfSpeech.PRZYMIOTNIK,
    "adv": PartOfSpeech.PRZYSŁÓWEK,
    "adja": PartOfSpeech.PRZYSŁÓWEK,
    "num": PartOfSpeech.LICZEBNIK,
    "numcomp": PartOfSpeech.LICZEBNIK,
    "frag": PartOfSpeech.LICZEBNIK,
    "ppron12": PartOfSpeech.ZAIMEK,
    "ppron3": PartOfSpeech.ZAIMEK,
    "siebie": PartOfSpeech.ZAIMEK,
    "prep": PartOfSpeech.PRZYIMEK,
    "conj": PartOfSpeech.SPÓJNIK,
    "part": PartOfSpeech.PARTYKUŁA,
    "comp": PartOfSpeech.PARTYKUŁA,
    "qub": PartOfSpeech.PARTYKUŁA,
    "interj": PartOfSpeech.WYKRZYKNIK,
    "fin": PartOfSpeech.CZASOWNIK,
    "bedzie": PartOfSpeech.CZASOWNIK,
    "aglt": PartOfSpeech.CZASOWNIK,
    "praet": PartOfSpeech.CZASOWNIK,
    "impt": PartOfSpeech.CZASOWNIK,
    "imps": PartOfSpeech.CZASOWNIK,
    "inf": PartOfSpeech.CZASOWNIK,
    "pcon": PartOfSpeech.CZASOWNIK,
    "pant": PartOfSpeech.CZASOWNIK,
    "pact": PartOfSpeech.CZASOWNIK,
    "pacta": PartOfSpeech.CZASOWNIK,
    "ppas": PartOfSpeech.CZASOWNIK,
    "ger": PartOfSpeech.CZASOWNIK,
    "winien": PartOfSpeech.CZASOWNIK,
    "pred": PartOfSpeech.CZASOWNIK,
    "brev": PartOfSpeech.INNY,
    "romandig": PartOfSpeech.INNY,
    "ign": PartOfSpeech.INNY,
    "xx": PartOfSpeech.INNY,
}

_CASE_CODES: Final[dict[str, Case]] = {
    "nom": Case.MIANOWNIK,
    "gen": Case.DOPEŁNIACZ,
    "dat": Case.CELOWNIK,
    "acc": Case.BIERNIK,
    "inst": Case.NARZĘDNIK,
    "loc": Case.MIEJSCOWNIK,
    "voc": Case.WOŁACZ,
}

_NUMBER_CODES: Final[dict[str, Number]] = {
    "sg": Number.POJEDYNCZA,
    "pl": Number.MNOGA,
}

_GENDER_CODES: Final[dict[str, Gender]] = {
    "m1": Gender.MĘSKOOSOBOWY,
    "m2": Gender.MĘSKOZWIERZĘCY,
    "m3": Gender.MĘSKORZECZOWY,
    "f": Gender.ŻEŃSKI,
    "n": Gender.NIJAKI,
    "n1": Gender.NIJAKI,
    "n2": Gender.NIJAKI,
}

_PERSON_CODES: Final[dict[str, Person]] = {
    "pri": Person.PIERWSZA,
    "sec": Person.DRUGA,
    "ter": Person.TRZECIA,
}

_ASPECT_CODES: Final[dict[str, Aspect]] = {
    "imperf": Aspect.NIEDOKONANY,
    "perf": Aspect.DOKONANY,
}

_DEGREE_CODES: Final[dict[str, Degree]] = {
    "pos": Degree.RÓWNY,
    "com": Degree.WYŻSZY,
    "sup": Degree.NAJWYŻSZY,
}

_Code = TypeVar("_Code", bound=StrEnum)


def part_of_speech(tag: str) -> PartOfSpeech:
    return _TAG_TO_PART.get(tag.split(":", 1)[0], PartOfSpeech.INNY)


def morph_tags(tag: str) -> MorphTags:
    prefix = tag.split(":", 1)[0]
    cases: set[Case] = set()
    genders: set[Gender] = set()
    aspects: set[Aspect] = set()
    extras: set[str] = set()
    number: Number | None = None
    person: Person | None = None
    degree: Degree | None = None
    negation: bool | None = None

    for segment in tag.split(":")[1:]:
        if segment in _NUMBER_CODES:
            number = _NUMBER_CODES[segment]
            continue
        if segment in _PERSON_CODES:
            person = _PERSON_CODES[segment]
            continue
        if segment in _DEGREE_CODES:
            degree = _DEGREE_CODES[segment]
            continue
        if segment == "aff":
            negation = False
            continue
        if segment == "neg":
            negation = True
            continue
        case_codes = _codes_of(segment, _CASE_CODES)
        if case_codes is not None:
            cases.update(case_codes)
            continue
        gender_codes = _codes_of(segment, _GENDER_CODES)
        if gender_codes is not None:
            genders.update(gender_codes)
            continue
        aspect_codes = _codes_of(segment, _ASPECT_CODES)
        if aspect_codes is not None:
            aspects.update(aspect_codes)
            continue
        extras.add(segment)

    parsed = MorphTags(
        cases=frozenset(cases),
        number=number,
        genders=frozenset(genders),
        person=person,
        aspects=frozenset(aspects),
        degree=degree,
        negation=negation,
        extras=frozenset(extras),
    )
    return _post_process(prefix, parsed)


def build_analysis(
    surface: str,
    lemma: str,
    tag: str,
    source: MorphSource,
    qualifiers: tuple[str, ...],
) -> Analysis:
    return Analysis(
        surface=surface,
        lemma=lemma,
        tag=tag,
        part=part_of_speech(tag),
        tags=morph_tags(tag),
        source=source,
        qualifiers=qualifiers,
    )


def _codes_of(segment: str, codes: dict[str, _Code]) -> frozenset[_Code] | None:
    parts = segment.split(".")
    if not all(part in codes for part in parts):
        return None
    return frozenset(codes[part] for part in parts)


def _post_process(prefix: str, tags: MorphTags) -> MorphTags:
    match prefix:
        case "depr":
            return tags.model_copy(update={"deprecative": True})
        case "fin":
            tense = Tense.PRZYSZŁY if Aspect.DOKONANY in tags.aspects else Tense.TERAŹNIEJSZY
            return tags.model_copy(
                update={
                    "verb_form": VerbForm.FORMA_OSOBOWA,
                    "tense": tense,
                    "mood": Mood.OZNAJMUJĄCY,
                }
            )
        case "bedzie":
            return tags.model_copy(
                update={
                    "verb_form": VerbForm.FORMA_OSOBOWA,
                    "tense": Tense.PRZYSZŁY,
                    "mood": Mood.OZNAJMUJĄCY,
                }
            )
        case "praet":
            return tags.model_copy(
                update={
                    "verb_form": VerbForm.FORMA_PRZESZŁA,
                    "tense": Tense.PRZESZŁY,
                    "mood": Mood.OZNAJMUJĄCY,
                }
            )
        case "impt":
            return tags.model_copy(
                update={
                    "verb_form": VerbForm.ROZKAŹNIK,
                    "mood": Mood.ROZKAZUJĄCY,
                }
            )
        case "imps":
            return tags.model_copy(update={"verb_form": VerbForm.BEZOSOBNIK})
        case "inf":
            return tags.model_copy(update={"verb_form": VerbForm.BEZOKOLICZNIK})
        case "pcon":
            return tags.model_copy(update={"verb_form": VerbForm.IMIESŁÓW_WSPÓŁCZESNY})
        case "pant":
            return tags.model_copy(update={"verb_form": VerbForm.IMIESŁÓW_UPRZEDNI})
        case "pact":
            return tags.model_copy(update={"verb_form": VerbForm.IMIESŁÓW_CZYNNY})
        case "pacta":
            return tags.model_copy(update={"verb_form": VerbForm.IMIESŁÓW_CZYNNY})
        case "ppas":
            return tags.model_copy(update={"verb_form": VerbForm.IMIESŁÓW_BIERNY})
        case "ger":
            return tags.model_copy(update={"verb_form": VerbForm.ODSŁOWNIK})
        case "aglt":
            return tags.model_copy(
                update={
                    "verb_form": VerbForm.KOŃCÓWKA_RUCHOMA,
                    "mood": Mood.PRZYPUSZCZAJĄCY,
                }
            )
        case "pred":
            return tags.model_copy(update={"verb_form": VerbForm.PREDYKATYW})
        case "winien":
            return tags.model_copy(
                update={
                    "verb_form": VerbForm.WINIEN,
                    "tense": Tense.TERAŹNIEJSZY,
                    "mood": Mood.OZNAJMUJĄCY,
                }
            )
        case "num":
            numeral_type = NumeralType.ZBIOROWY if "col" in tags.extras else NumeralType.GŁÓWNY
            return tags.model_copy(update={"numeral_type": numeral_type})
        case "ppron12" | "ppron3":
            return tags.model_copy(update={"pronoun_type": PronounType.OSOBOWY})
        case "siebie":
            return tags.model_copy(update={"pronoun_type": PronounType.ZWROTNY})
        case _:
            return tags
