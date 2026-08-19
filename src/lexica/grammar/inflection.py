from lexica.grammar.aspect import Aspect
from lexica.grammar.case import Case
from lexica.grammar.degree import Degree
from lexica.grammar.gender import Gender
from lexica.grammar.mood import Mood
from lexica.grammar.number import Number
from lexica.grammar.numeral_type import NumeralType
from lexica.grammar.person import Person
from lexica.grammar.pronoun_type import PronounType
from lexica.grammar.quality import Quality
from lexica.grammar.tense import Tense
from lexica.grammar.verb_form import VerbForm
from wordcore.models.base import BaseFrozen


class Inflection(BaseFrozen):
    cases: frozenset[Case]
    governed_case: Case | None
    numbers: frozenset[Number]
    genders: frozenset[Gender]
    person: Person | None
    tense: Tense | None
    mood: Mood | None
    aspects: frozenset[Aspect]
    degree: Degree | None
    verb_form: VerbForm | None
    numeral_type: NumeralType | None
    pronoun_type: PronounType | None
    negation: bool | None
    deprecative: bool
    qualities: frozenset[Quality]
