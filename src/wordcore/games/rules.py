import random
from abc import ABC, abstractmethod

from wordcore.moves.move import Move
from wordcore.positions.position import Position


class Rules(ABC):
    @abstractmethod
    def initial_position(self, rng: random.Random) -> Position:
        raise NotImplementedError

    @abstractmethod
    def validate(self, position: Position, move: Move) -> None:
        raise NotImplementedError

    @abstractmethod
    def apply(
        self,
        position: Position,
        move: Move,
        rng: random.Random,
    ) -> Position:
        raise NotImplementedError

    def legal_moves(self, _position: Position, _seat: int) -> tuple[Move, ...]:
        return ()
