from collections.abc import Iterable

from lexica.grammar.aspect import Aspect
from lexica.grammar.case import Case
from lexica.grammar.degree import Degree
from lexica.grammar.gender import Gender
from lexica.grammar.inflection import Inflection
from lexica.grammar.mood import Mood
from lexica.grammar.number import Number
from lexica.grammar.numeral_type import NumeralType
from lexica.grammar.person import Person
from lexica.grammar.pronoun_type import PronounType
from lexica.grammar.quality import Quality
from lexica.grammar.tense import Tense
from lexica.grammar.verb_form import VerbForm


def an_inflection(
    *,
    cases: Iterable[Case] = (),
    governed_case: Case | None = None,
    numbers: Iterable[Number] = (),
    genders: Iterable[Gender] = (),
    person: Person | None = None,
    tense: Tense | None = None,
    mood: Mood | None = None,
    aspects: Iterable[Aspect] = (),
    degree: Degree | None = None,
    verb_form: VerbForm | None = None,
    numeral_type: NumeralType | None = None,
    pronoun_type: PronounType | None = None,
    negation: bool | None = None,
    deprecative: bool = False,
    qualities: Iterable[Quality] = (),
) -> Inflection:
    return Inflection(
        cases=frozenset(cases),
        governed_case=governed_case,
        numbers=frozenset(numbers),
        genders=frozenset(genders),
        person=person,
        tense=tense,
        mood=mood,
        aspects=frozenset(aspects),
        degree=degree,
        verb_form=verb_form,
        numeral_type=numeral_type,
        pronoun_type=pronoun_type,
        negation=negation,
        deprecative=deprecative,
        qualities=frozenset(qualities),
    )
