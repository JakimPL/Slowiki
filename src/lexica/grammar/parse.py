from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Final, NamedTuple, TypeVar

from lexica.grammar.aspect import Aspect
from lexica.grammar.case import Case
from lexica.grammar.degree import Degree
from lexica.grammar.dialect import TagsetDialect
from lexica.grammar.gender import Gender
from lexica.grammar.inflection import Inflection
from lexica.grammar.mood import Mood
from lexica.grammar.number import Number
from lexica.grammar.numeral_type import NumeralType
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.grammar.person import Person
from lexica.grammar.pronoun_type import PronounType
from lexica.grammar.quality import Quality
from lexica.grammar.segments import SegmentTable
from lexica.grammar.tables import segment_table
from lexica.grammar.tense import Tense
from lexica.grammar.verb_form import VerbForm
from wordcore.errors.exceptions import InvalidConfiguration

SEGMENT_SEPARATOR: Final = ":"
ALTERNATIVE_SEPARATOR: Final = "."

_NEGATIONS: Final[Mapping[str, bool]] = {"aff": False, "neg": True}

_NUMERAL_PREFIX: Final = "num"

_VERB_FORMS: Final[Mapping[str, VerbForm]] = {
    "inf": VerbForm.BEZOKOLICZNIK,
    "fin": VerbForm.FORMA_OSOBOWA,
    "bedzie": VerbForm.FORMA_OSOBOWA,
    "praet": VerbForm.FORMA_PRZESZŁA,
    "cond": VerbForm.FORMA_PRZYPUSZCZAJĄCA,
    "impt": VerbForm.ROZKAŹNIK,
    "imps": VerbForm.BEZOSOBNIK,
    "pcon": VerbForm.IMIESŁÓW_WSPÓŁCZESNY,
    "pant": VerbForm.IMIESŁÓW_UPRZEDNI,
    "pact": VerbForm.IMIESŁÓW_CZYNNY,
    "pacta": VerbForm.IMIESŁÓW_CZYNNY,
    "ppas": VerbForm.IMIESŁÓW_BIERNY,
    "ger": VerbForm.ODSŁOWNIK,
    "aglt": VerbForm.KOŃCÓWKA_RUCHOMA,
    "pred": VerbForm.PREDYKATYW,
    "winien": VerbForm.WINIEN,
}

_MOODS: Final[Mapping[str, Mood]] = {
    "fin": Mood.OZNAJMUJĄCY,
    "bedzie": Mood.OZNAJMUJĄCY,
    "praet": Mood.OZNAJMUJĄCY,
    "winien": Mood.OZNAJMUJĄCY,
    "impt": Mood.ROZKAZUJĄCY,
    "cond": Mood.PRZYPUSZCZAJĄCY,
}

_TENSES: Final[Mapping[str, Tense]] = {
    "praet": Tense.PRZESZŁY,
    "bedzie": Tense.PRZYSZŁY,
    "winien": Tense.TERAŹNIEJSZY,
}

_ASPECT_TENSE_PREFIXES: Final[frozenset[str]] = frozenset({"fin"})

_PRONOUN_TYPES: Final[Mapping[str, PronounType]] = {
    "ppron12": PronounType.OSOBOWY,
    "ppron3": PronounType.OSOBOWY,
    "siebie": PronounType.ZWROTNY,
}

_DEPRECATIVE_PREFIXES: Final[frozenset[str]] = frozenset({"depr"})

_GOVERNING_PREFIXES: Final[frozenset[str]] = frozenset({"prep"})

_IMPLIED_QUALITIES: Final[Mapping[str, frozenset[Quality]]] = {
    "adja": frozenset({Quality.ZŁOŻONY}),
    "numcomp": frozenset({Quality.ZŁOŻONY}),
    "adjp": frozenset({Quality.POPRZYIMKOWY}),
}

_Code = TypeVar("_Code", bound=StrEnum)


class TagSegments(NamedTuple):
    cases: frozenset[Case]
    numbers: frozenset[Number]
    genders: frozenset[Gender]
    person: Person | None
    aspects: frozenset[Aspect]
    degree: Degree | None
    negation: bool | None
    qualities: frozenset[Quality]


def part_of_speech(tag: str, dialect: TagsetDialect) -> PartOfSpeech:
    table = segment_table(dialect)
    prefix = tag_prefix(tag)
    _ensure_prefix_named(tag, dialect, prefix, table)
    return table.parts[prefix]


def inflection_of(tag: str, dialect: TagsetDialect) -> Inflection:
    table = segment_table(dialect)
    prefix = tag_prefix(tag)
    _ensure_prefix_named(tag, dialect, prefix, table)
    segments = tag_segments(tag, dialect, table)
    return Inflection(
        cases=frozenset() if prefix in _GOVERNING_PREFIXES else segments.cases,
        governed_case=_governed_case(tag, prefix, segments.cases),
        numbers=segments.numbers,
        genders=segments.genders,
        person=segments.person,
        tense=_tense(prefix, segments.aspects),
        mood=_MOODS.get(prefix),
        aspects=segments.aspects,
        degree=segments.degree,
        verb_form=_VERB_FORMS.get(prefix),
        numeral_type=_numeral_type(prefix, segments.qualities),
        pronoun_type=_PRONOUN_TYPES.get(prefix),
        negation=segments.negation,
        deprecative=prefix in _DEPRECATIVE_PREFIXES,
        qualities=segments.qualities | _IMPLIED_QUALITIES.get(prefix, frozenset()),
    )


def tag_prefix(tag: str) -> str:
    return tag.split(SEGMENT_SEPARATOR, 1)[0]


def tag_segments(tag: str, dialect: TagsetDialect, table: SegmentTable) -> TagSegments:
    cases: set[Case] = set()
    numbers: set[Number] = set()
    genders: set[Gender] = set()
    aspects: set[Aspect] = set()
    qualities: set[Quality] = set()
    person: Person | None = None
    degree: Degree | None = None
    negation: bool | None = None

    for segment in tag.split(SEGMENT_SEPARATOR)[1:]:
        alternatives = tuple(segment.split(ALTERNATIVE_SEPARATOR))
        if segment in _NEGATIONS:
            negation = _NEGATIONS[segment]
        elif _spans(alternatives, table.cases):
            cases.update(_values(alternatives, table.cases))
        elif _spans(alternatives, table.numbers):
            numbers.update(_values(alternatives, table.numbers))
        elif _spans(alternatives, table.genders):
            genders.update(_united(alternatives, table.genders))
        elif _spans(alternatives, table.persons):
            person = table.persons[_only(tag, segment, alternatives)]
        elif _spans(alternatives, table.aspects):
            aspects.update(_values(alternatives, table.aspects))
        elif _spans(alternatives, table.degrees):
            degree = table.degrees[_only(tag, segment, alternatives)]
        elif _spans(alternatives, table.qualities):
            qualities.update(_values(alternatives, table.qualities))
        else:
            raise InvalidConfiguration(
                f"the {dialect} tagset carries no segment {segment} in the tag {tag}"
            )

    return TagSegments(
        cases=frozenset(cases),
        numbers=frozenset(numbers),
        genders=frozenset(genders),
        person=person,
        aspects=frozenset(aspects),
        degree=degree,
        negation=negation,
        qualities=frozenset(qualities),
    )


def _governed_case(tag: str, prefix: str, cases: frozenset[Case]) -> Case | None:
    if prefix not in _GOVERNING_PREFIXES:
        return None
    if len(cases) > 1:
        raise InvalidConfiguration(f"the tag {tag} governs {len(cases)} cases at once")
    return next(iter(cases), None)


def _tense(prefix: str, aspects: frozenset[Aspect]) -> Tense | None:
    if prefix in _ASPECT_TENSE_PREFIXES:
        return Tense.PRZYSZŁY if Aspect.DOKONANY in aspects else Tense.TERAŹNIEJSZY
    return _TENSES.get(prefix)


def _numeral_type(prefix: str, qualities: frozenset[Quality]) -> NumeralType | None:
    if prefix != _NUMERAL_PREFIX:
        return None
    return NumeralType.ZBIOROWY if Quality.ZBIOROWY in qualities else NumeralType.GŁÓWNY


def _spans(alternatives: Sequence[str], codes: Mapping[str, object]) -> bool:
    return all(code in codes for code in alternatives)


def _values(alternatives: Sequence[str], codes: Mapping[str, _Code]) -> frozenset[_Code]:
    return frozenset(codes[code] for code in alternatives)


def _united(
    alternatives: Sequence[str],
    codes: Mapping[str, frozenset[_Code]],
) -> frozenset[_Code]:
    return frozenset(value for code in alternatives for value in codes[code])


def _only(tag: str, segment: str, alternatives: Sequence[str]) -> str:
    if len(alternatives) > 1:
        raise InvalidConfiguration(
            f"the segment {segment} in the tag {tag} states one value at most"
        )
    return alternatives[0]


def _ensure_prefix_named(
    tag: str,
    dialect: TagsetDialect,
    prefix: str,
    table: SegmentTable,
) -> None:
    if prefix not in table.parts:
        raise InvalidConfiguration(
            f"the {dialect} tagset names no part of speech for {prefix} in the tag {tag}"
        )
