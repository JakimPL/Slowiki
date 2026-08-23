from pathlib import Path

import yaml

from lexica.grammar.aspect import Aspect
from lexica.grammar.case import Case
from lexica.grammar.degree import Degree
from lexica.grammar.gender import Gender
from lexica.grammar.inflection import Inflection
from lexica.grammar.mood import Mood
from lexica.grammar.number import Number
from lexica.grammar.numeral_type import NumeralType
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.grammar.person import Person
from lexica.grammar.tense import Tense
from lexica.grammar.verb_form import VerbForm
from wordcore.models.base import BaseFrozen


class SurfaceClaim(BaseFrozen):
    cases: frozenset[Case] = frozenset()
    numbers: frozenset[Number] = frozenset()
    genders: frozenset[Gender] = frozenset()
    aspects: frozenset[Aspect] = frozenset()
    governed_case: Case | None = None
    person: Person | None = None
    tense: Tense | None = None
    mood: Mood | None = None
    degree: Degree | None = None
    verb_form: VerbForm | None = None
    numeral_type: NumeralType | None = None
    deprecative: bool | None = None

    def holds_for(self, tags: Inflection) -> bool:
        return (
            self.cases <= tags.cases
            and self.numbers <= tags.numbers
            and self.genders <= tags.genders
            and self.aspects <= tags.aspects
            and _agrees(self.governed_case, tags.governed_case)
            and _agrees(self.person, tags.person)
            and _agrees(self.tense, tags.tense)
            and _agrees(self.mood, tags.mood)
            and _agrees(self.degree, tags.degree)
            and _agrees(self.verb_form, tags.verb_form)
            and _agrees(self.numeral_type, tags.numeral_type)
            and _agrees(self.deprecative, tags.deprecative)
        )


class ReadingClaim(BaseFrozen):
    part: PartOfSpeech
    base: str
    surface: SurfaceClaim | None = None
    contains: tuple[str, ...] = ()

    @property
    def lexeme(self) -> tuple[PartOfSpeech, str]:
        return self.part, self.base


class DeniedReading(BaseFrozen):
    part: PartOfSpeech
    base: str

    @property
    def lexeme(self) -> tuple[PartOfSpeech, str]:
        return self.part, self.base


class Specimen(BaseFrozen):
    word: str
    readings: tuple[ReadingClaim, ...]
    denied: tuple[DeniedReading, ...] = ()
    absent: tuple[str, ...] = ()
    note: str = ""


class Oracle(BaseFrozen):
    dict_id: str
    specimens: tuple[Specimen, ...]


def read_oracle(path: Path) -> Oracle:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Oracle(
        dict_id=document["dict_id"],
        specimens=tuple(_specimen_of(entry) for entry in document["specimens"]),
    )


def _specimen_of(entry: dict[str, object]) -> Specimen:
    return Specimen(
        word=_text(entry["word"]).upper(),
        readings=tuple(_reading_of(claim) for claim in _claims(entry.get("readings"))),
        denied=tuple(_denial_of(claim) for claim in _claims(entry.get("denied"))),
        absent=tuple(_text(form).upper() for form in _sequence(entry.get("absent"))),
        note=_text(entry.get("note", "")),
    )


def _reading_of(claim: dict[str, object]) -> ReadingClaim:
    surface = claim.get("surface")
    return ReadingClaim(
        part=PartOfSpeech(_text(claim["part"])),
        base=_text(claim["base"]).upper(),
        surface=SurfaceClaim.model_validate(surface) if surface is not None else None,
        contains=tuple(_text(form).upper() for form in _sequence(claim.get("contains"))),
    )


def _denial_of(claim: dict[str, object]) -> DeniedReading:
    return DeniedReading(part=PartOfSpeech(_text(claim["part"])), base=_text(claim["base"]).upper())


def _claims(value: object) -> list[dict[str, object]]:
    if value is None:
        return []

    assert isinstance(value, list), value
    return [claim for claim in value if isinstance(claim, dict)]


def _sequence(value: object) -> list[object]:
    if value is None:
        return []

    assert isinstance(value, list), value
    return list(value)


def _text(value: object) -> str:
    assert isinstance(value, str), value
    return value


def _agrees(claimed: object, actual: object) -> bool:
    return claimed is None or claimed == actual
