from collections.abc import Mapping

from lexica.grammar.aspect import Aspect
from lexica.grammar.case import Case
from lexica.grammar.degree import Degree
from lexica.grammar.gender import Gender
from lexica.grammar.number import Number
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.grammar.person import Person
from lexica.grammar.quality import Quality
from wordcore.models.base import BaseFrozen


class SegmentTable(BaseFrozen):
    parts: Mapping[str, PartOfSpeech]
    cases: Mapping[str, Case]
    numbers: Mapping[str, Number]
    genders: Mapping[str, frozenset[Gender]]
    persons: Mapping[str, Person]
    aspects: Mapping[str, Aspect]
    degrees: Mapping[str, Degree]
    qualities: Mapping[str, Quality]
