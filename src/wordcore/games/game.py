import random
from abc import ABC, abstractmethod

from wordcore.exceptions import (
    GameOver,
    IllegalMove,
    NotYourTurn,
    RejectionCode,
    StalePosition,
    WordcoreError,
    rejection_code,
)
from wordcore.games.journal import EntryKind, JournalEntry
from wordcore.moves.action import ActionKind, Move
from wordcore.positions.position import Position
from wordcore.states.state import Phase
from wordcore.views.events import EventView, event_view
from wordcore.views.projection import PositionView, project


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
        self._initial = rules.initial_position(rng)
        self._entries: list[JournalEntry] = []

    @property
    def position(self) -> Position:
        if self._entries:
            return self._entries[-1].position
        return self._initial

    @property
    def seq(self) -> int:
        return len(self._entries)

    def view(self, observer: int | None) -> PositionView:
        return project(self.position, observer)

    def events(self, observer: int | None, since: int) -> tuple[EventView, ...]:
        return tuple(
            event_view(entry, index, observer)
            for index, entry in enumerate(self._entries)
            if index >= since
        )

    def submit(self, move: Move, base_seq: int, premove: bool = False) -> JournalEntry:
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

    def _queue_premove(self, position: Position, move: Move) -> JournalEntry:
        self._ensure_member(position, move.player)
        self._rules.validate(position, move)
        new_position = position.model_copy(
            update={"state": position.state.with_premove(move.player, move)}
        )
        return self._record(EntryKind.PREMOVE_SET, move, move.player, None, new_position)

    def _play_move(self, position: Position, move: Move) -> JournalEntry:
        self._ensure_member(position, move.player)
        if move.player not in position.state.to_act:
            raise NotYourTurn("player is not on turn")
        self._rules.validate(position, move)
        new_position = self._rules.apply(position, move, self._rng)
        entry = self._record(EntryKind.MOVE, move, move.player, None, new_position)
        if move.action.kind != ActionKind.REORDER:
            self._settle_premoves()
        return entry

    def _ensure_member(self, position: Position, player: int) -> None:
        if player not in position.players:
            raise IllegalMove("player is not part of the game")

    def _record(
        self,
        kind: EntryKind,
        move: Move | None,
        actor: int | None,
        reason: RejectionCode | None,
        position: Position,
    ) -> JournalEntry:
        entry = JournalEntry(kind=kind, move=move, actor=actor, reason=reason, position=position)
        self._entries.append(entry)
        return entry

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
            self._record(EntryKind.MOVE, pending, seat, None, new_position)
        except WordcoreError as error:
            new_position = position.model_copy(
                update={"state": position.state.without_premove(seat)}
            )
            self._record(
                EntryKind.PREMOVE_DISCARDED, None, seat, rejection_code(error), new_position
            )
        return True
