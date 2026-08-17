from wordcore.board.board import Board
from wordcore.board.bonus import Bonus, BonusKind
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen


class BonusSpec(BaseFrozen):
    kind: BonusKind
    multiplier: int
    category: str | None = None
    positions: tuple[tuple[int, int], ...]


class BoardPreset(BaseFrozen):
    name: str
    size: int
    bonuses: tuple[BonusSpec, ...]


def get_bonus_index(row: int, column: int, preset: BoardPreset) -> int:
    if not (0 <= row < preset.size and 0 <= column < preset.size):
        raise InvalidConfiguration("bonus square outside the board")

    return row * preset.size + column


def board_from_preset(preset: BoardPreset) -> Board:
    bonuses: list[Bonus | None] = [None] * (preset.size * preset.size)
    for spec in preset.bonuses:
        for row, column in spec.positions:
            index = get_bonus_index(row, column, preset)
            if bonuses[index] is not None:
                raise InvalidConfiguration("two bonuses on one square")

            bonuses[index] = Bonus(
                kind=spec.kind,
                multiplier=spec.multiplier,
                category=spec.category,
            )

    tiles = (None,) * (preset.size * preset.size)
    return Board(size=preset.size, bonuses=tuple(bonuses), tiles=tiles)
