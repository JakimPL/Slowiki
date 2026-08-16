from typing import Protocol

from wordcore.moves.action import Move
from wordcore.positions.position import Position


class Bot(Protocol):
    def choose(self, position: Position, seat: int) -> Move:
        ...
