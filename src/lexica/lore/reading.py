from lexica.grammar.inflection import Inflection
from lexica.grammar.part_of_speech import PartOfSpeech
from wordcore.models.base import BaseFrozen


class InflectedForm(BaseFrozen):
    text: str
    tags: Inflection
    playable: bool


class LoreReading(BaseFrozen):
    lexeme: str
    part: PartOfSpeech
    base: str
    forms: tuple[InflectedForm, ...]


class WordLore(BaseFrozen):
    word: str
    playable: bool
    readings: tuple[LoreReading, ...]
