from wordcore.models.base import BaseFrozen
from wordcore.models.letters import (
    CanonicalLetter,
    CanonicalSymbol,
    CategoryName,
    LetterValue,
    TileCount,
)


class Letter(BaseFrozen):
    symbol: CanonicalSymbol
    value: LetterValue
    category: CategoryName


class LetterSpec(BaseFrozen):
    symbol: CanonicalSymbol
    value: LetterValue
    category: CategoryName
    count: TileCount


class Tile(BaseFrozen):
    identifier: int
    letter: CanonicalLetter
    value: LetterValue
    category: CategoryName
    blank: bool
