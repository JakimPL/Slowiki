from typing import Protocol

from wordcore.moves.move import Move
from wordcore.positions.position import Position


class Bot(Protocol):
    def choose(self, position: Position, seat: int) -> Move: ...
