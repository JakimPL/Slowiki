from wordcore.board.board import Bonus, BonusKind, Board
from wordcore.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen


class BonusSpec(BaseFrozen):
    kind: BonusKind
    multiplier: int
    category: str | None = None
    row: int
    column: int


class BoardPreset(BaseFrozen):
    name: str
    size: int
    bonuses: tuple[BonusSpec, ...]


def board_from_preset(preset: BoardPreset) -> Board:
    bonuses: list[Bonus | None] = [None] * (preset.size * preset.size)
    for spec in preset.bonuses:
        if not (0 <= spec.row < preset.size and 0 <= spec.column < preset.size):
            raise InvalidConfiguration("bonus square outside the board")
        index = spec.row * preset.size + spec.column
        if bonuses[index] is not None:
            raise InvalidConfiguration("two bonuses on one square")
        bonuses[index] = Bonus(kind=spec.kind, multiplier=spec.multiplier, category=spec.category)
    tiles = (None,) * (preset.size * preset.size)
    return Board(size=preset.size, bonuses=tuple(bonuses), tiles=tiles)
