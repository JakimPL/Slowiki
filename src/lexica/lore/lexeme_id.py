from typing import Final

from lexica.grammar.part_of_speech import PartOfSpeech
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen

TOKEN_SEPARATOR: Final = ":"
PATTERN_SEPARATOR: Final = ":"

_TOKEN_FIELDS: Final = 3


class LexemeId(BaseFrozen):
    part: PartOfSpeech
    lemma: str
    pattern: str


def lexeme_id_from_lemma(part: PartOfSpeech, lemma: str) -> LexemeId:
    written, _, pattern = lemma.partition(PATTERN_SEPARATOR)
    return LexemeId(part=part, lemma=written.upper(), pattern=pattern)


def lexeme_id_from_token(token: str) -> LexemeId:
    fields = token.split(TOKEN_SEPARATOR, _TOKEN_FIELDS - 1)
    if len(fields) != _TOKEN_FIELDS:
        raise InvalidConfiguration(f"the lexeme token {token} states {len(fields)} fields")
    part, lemma, pattern = fields
    return LexemeId(part=PartOfSpeech(part), lemma=lemma, pattern=pattern)


def token_of(identifier: LexemeId) -> str:
    return TOKEN_SEPARATOR.join((identifier.part.value, identifier.lemma, identifier.pattern))
