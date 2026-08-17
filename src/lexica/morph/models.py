from enum import StrEnum

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
from wordcore.models.base import BaseFrozen


class MorphSource(StrEnum):
    SGJP = "sgjp"
    POLIMORF = "polimorf"


class MorphTags(BaseFrozen):
    cases: frozenset[Case] = frozenset()
    number: Number | None = None
    genders: frozenset[Gender] = frozenset()
    person: Person | None = None
    tense: Tense | None = None
    mood: Mood | None = None
    aspects: frozenset[Aspect] = frozenset()
    degree: Degree | None = None
    verb_form: VerbForm | None = None
    numeral_type: NumeralType | None = None
    pronoun_type: PronounType | None = None
    negation: bool | None = None
    deprecative: bool = False
    extras: frozenset[str] = frozenset()


class Analysis(BaseFrozen):
    surface: str
    lemma: str
    tag: str
    part: PartOfSpeech
    tags: MorphTags
    source: MorphSource
    qualifiers: tuple[str, ...] = ()


class VariantRecord(BaseFrozen):
    form: str
    tags: MorphTags
    in_dictionary: bool


class ClassRecord(BaseFrozen):
    class_id: str
    part: PartOfSpeech
    lemma: str
    base: str
    variants: tuple[VariantRecord, ...]


def class_key(lemma: str, part: PartOfSpeech) -> str:
    return f"{part.value}:{lemma}"
