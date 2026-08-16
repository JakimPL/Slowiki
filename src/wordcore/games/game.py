import random
from abc import ABC, abstractmethod

from wordcore.exceptions import GameOver, IllegalMove, NotYourTurn, StalePosition, WordcoreError
from wordcore.models.base import BaseFrozen
from wordcore.moves.action import ActionKind, Move
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
        position = self._require_current(base_seq)
        if premove and move.player not in position.state.to_act:
            return self._queue_premove(position, move)
        return self._play_move(position, move)

    def _require_current(self, base_seq: int) -> Position:
        if base_seq != self.seq:
            raise StalePosition("position advanced past the submitted sequence")
        position = self.position
        if position.state.phase == Phase.GAME_OVER:
            raise GameOver("the game has finished")
        return position

    def _queue_premove(self, position: Position, move: Move) -> Transaction:
        self._ensure_member(position, move.player)
        self._rules.validate(position, move)
        new_position = position.model_copy(
            update={"state": position.state.with_premove(move.player, move)}
        )
        self._record(move, new_position)
        return Transaction(seq=self.seq - 1, move=move, position=new_position)

    def _play_move(self, position: Position, move: Move) -> Transaction:
        self._ensure_member(position, move.player)
        if move.player not in position.state.to_act:
            raise NotYourTurn("player is not on turn")
        self._rules.validate(position, move)
        new_position = self._rules.apply(position, move, self._rng)
        self._record(move, new_position)
        move_seq = self.seq - 1
        if move.action.kind != ActionKind.REORDER:
            self._settle_premoves()
        return Transaction(seq=move_seq, move=move, position=self.position)

    def _ensure_member(self, position: Position, player: int) -> None:
        if player not in position.players:
            raise IllegalMove("player is not part of the game")

    def _record(self, move: Move | None, position: Position) -> None:
        self._moves.append(move)
        self._history.append(position)

    def _settle_premoves(self) -> None:
        for _ in range(len(self.position.players)):
            if not self._settle_next_premove():
                return

    def _settle_next_premove(self) -> bool:
        position = self.position
        if position.state.phase == Phase.GAME_OVER:
            return False
        if len(position.state.to_act) != 1:
            return False
        seat = next(iter(position.state.to_act))
        pending = position.state.premoves.get(seat)
        if pending is None:
            return False
        try:
            self._rules.validate(position, pending)
            applied = self._rules.apply(position, pending, self._rng)
            new_position = applied.model_copy(update={"state": applied.state.without_premove(seat)})
            self._record(pending, new_position)
        except WordcoreError:
            new_position = position.model_copy(
                update={"state": position.state.without_premove(seat)}
            )
            self._record(None, new_position)
        return True
