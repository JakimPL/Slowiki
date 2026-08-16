from wordcore.models.base import BaseFrozen
from wordcore.models.letters import CanonicalLetter


class Letter(BaseFrozen):
    symbol: CanonicalLetter
    value: int
    category: str


class LetterSpec(BaseFrozen):
    symbol: CanonicalLetter
    value: int
    category: str
    count: int


class Tile(BaseFrozen):
    identifier: int
    letter: CanonicalLetter
    value: int
    category: str
    blank: bool


class TilePreset(BaseFrozen):
    name: str
    letters: tuple[LetterSpec, ...]
    blanks: int
    rack_size: int | None
