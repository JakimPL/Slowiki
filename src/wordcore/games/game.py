import random
from abc import ABC, abstractmethod

from wordcore.exceptions import GameOver, IllegalMove, NotYourTurn, StalePosition, WordcoreError
from wordcore.models.base import BaseFrozen
from wordcore.moves.action import Move
from wordcore.positions.position import Position
from wordcore.states.state import Phase
from wordcore.views.projection import PositionView, project


class Transaction(BaseFrozen):
    seq: int
    move: Move | None
    position: Position


class EventView(BaseFrozen):
    seq: int
    move: Move | None
    position: PositionView


class Rules(ABC):
    @abstractmethod
    def initial_position(self, rng: random.Random) -> Position:
        raise NotImplementedError

    @abstractmethod
    def validate(self, position: Position, move: Move) -> None:
        raise NotImplementedError

    @abstractmethod
    def apply(self, position: Position, move: Move, rng: random.Random) -> Position:
        raise NotImplementedError

    def legal_moves(self, _position: Position, _seat: int) -> tuple[Move, ...]:
        return ()


class Game:
    def __init__(self, rules: Rules, rng: random.Random) -> None:
        self._rules = rules
        self._rng = rng
        self._history: list[Position] = [rules.initial_position(rng)]
        self._moves: list[Move | None] = []

    @property
    def position(self) -> Position:
        return self._history[-1]

    @property
    def seq(self) -> int:
        return len(self._moves)

    def view(self, observer: int | None) -> PositionView:
        return project(self.position, observer)

    def events(self, observer: int | None, since: int) -> tuple[EventView, ...]:
        return tuple(
            EventView(
                seq=index,
                move=self._moves[index],
                position=project(self._history[index + 1], observer),
            )
            for index in range(since, len(self._moves))
        )

    def submit(self, move: Move, base_seq: int, premove: bool = False) -> Transaction:
        if base_seq != self.seq:
            raise StalePosition("position advanced past the submitted sequence")
        position = self.position
        if position.state.phase == Phase.GAME_OVER:
            raise GameOver("the game has finished")
        if move.player not in position.players:
            raise IllegalMove("player is not part of the game")
        if premove and move.player not in position.state.to_act:
            self._rules.validate(position, move)
            new_state = position.state.model_copy(
                update={"premoves": {**position.state.premoves, move.player: move}}
            )
            new_position = position.model_copy(update={"state": new_state})
            self._record(move, new_position)
            return Transaction(seq=self.seq - 1, move=move, position=new_position)
        if move.player not in position.state.to_act:
            raise NotYourTurn("player is not on turn")
        self._rules.validate(position, move)
        new_position = self._rules.apply(position, move, self._rng)
        self._record(move, new_position)
        move_seq = self.seq - 1
        self._settle_premoves()
        return Transaction(seq=move_seq, move=move, position=self.position)

    def _record(self, move: Move | None, position: Position) -> None:
        self._moves.append(move)
        self._history.append(position)

    def _settle_premoves(self) -> None:
        while True:
            position = self.position
            if position.state.phase == Phase.GAME_OVER:
                return
            if len(position.state.to_act) != 1:
                return
            seat = next(iter(position.state.to_act))
            pending = position.state.premoves.get(seat)
            if pending is None:
                return
            try:
                self._rules.validate(position, pending)
                applied = self._rules.apply(position, pending, self._rng)
                cleared_state = applied.state.model_copy(
                    update={"premoves": {**applied.state.premoves, seat: None}}
                )
                new_position = applied.model_copy(update={"state": cleared_state})
                self._record(pending, new_position)
            except WordcoreError:
                new_state = position.state.model_copy(
                    update={"premoves": {**position.state.premoves, seat: None}}
                )
                new_position = position.model_copy(update={"state": new_state})
                self._record(None, new_position)
