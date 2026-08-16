from wordcore.models.base import BaseFrozen


class Letter(BaseFrozen):
    symbol: str
    value: int
    category: str


class LetterSpec(BaseFrozen):
    symbol: str
    value: int
    category: str
    count: int


class Tile(BaseFrozen):
    identifier: int
    letter: str
    value: int
    category: str
    blank: bool


class TilePreset(BaseFrozen):
    name: str
    letters: tuple[LetterSpec, ...]
    blanks: int
    rack_size: int | None
