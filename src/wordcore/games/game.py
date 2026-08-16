import random

from wordcore.exceptions import (
    GameOver,
    IllegalMove,
    NoPremove,
    NotYourTurn,
    RejectionCode,
    StalePosition,
    WordcoreError,
    rejection_code,
)
from wordcore.games.journal import JournalEntry
from wordcore.games.kind import EntryKind
from wordcore.games.rules import Rules
from wordcore.moves.kind import ActionKind
from wordcore.moves.move import Move
from wordcore.positions.position import Position
from wordcore.states.state import Phase
from wordcore.views.events import EventView, event_view
from wordcore.views.projection import PositionView, project


class Game:
    def __init__(
        self,
        rules: Rules,
        rng: random.Random,
        premoves_allowed: bool,
    ) -> None:
        self._rules = rules
        self._rng = rng
        self._premoves_allowed = premoves_allowed
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
        self._ensure_member(position, move.player)
        if premove and move.player not in position.state.to_act:
            self._ensure_premoves_allowed()
            return self._queue_premove(position, move)

        return self._play_move(position, move)

    def cancel_premove(self, player: int, base_seq: int) -> JournalEntry:
        position = self._require_current(base_seq)
        self._ensure_member(position, player)
        if position.state.premoves.get(player) is None:
            raise NoPremove("no premove is queued")

        return self._record(
            kind=EntryKind.PREMOVE_CLEARED,
            move=None,
            actor=player,
            reason=None,
            position=_without_premove(position, player),
        )

    def _require_current(self, base_seq: int) -> Position:
        if base_seq != self.seq:
            raise StalePosition("position advanced past the submitted sequence")

        position = self.position
        if position.state.phase == Phase.GAME_OVER:
            raise GameOver("the game has finished")

        return position

    def _ensure_member(self, position: Position, player: int) -> None:
        if player not in position.players:
            raise IllegalMove("player is not part of the game")

    def _ensure_premoves_allowed(self) -> None:
        if not self._premoves_allowed:
            raise IllegalMove("premoves are disabled at this table")

    def _queue_premove(self, position: Position, move: Move) -> JournalEntry:
        self._rules.validate(position, move)
        return self._record(
            kind=EntryKind.PREMOVE_SET,
            move=move,
            actor=move.player,
            reason=None,
            position=_with_premove(position, move),
        )

    def _play_move(self, position: Position, move: Move) -> JournalEntry:
        if move.player not in position.state.to_act:
            raise NotYourTurn("player is not on turn")

        self._rules.validate(position, move)
        entry = self._record(
            kind=EntryKind.MOVE,
            move=move,
            actor=move.player,
            reason=None,
            position=self._rules.apply(position, move, self._rng),
        )
        if move.action.kind != ActionKind.REORDER:
            self._settle_premoves()

        return entry

    def _settle_premoves(self) -> None:
        for _ in range(len(self.position.players)):
            if not self._settle_next_premove():
                return

    def _settle_next_premove(self) -> bool:
        position = self.position
        seat = _sole_actor(position)
        if seat is None:
            return False

        pending = position.state.premoves.get(seat)
        if pending is None:
            return False

        self._resolve_premove(position, seat, pending)
        return True

    def _resolve_premove(self, position: Position, seat: int, pending: Move) -> None:
        try:
            self._rules.validate(position, pending)
        except WordcoreError as error:
            self._record(
                kind=EntryKind.PREMOVE_DISCARDED,
                move=None,
                actor=seat,
                reason=rejection_code(error),
                position=_without_premove(position, seat),
            )
            return

        applied = self._rules.apply(position, pending, self._rng)
        self._record(
            kind=EntryKind.MOVE,
            move=pending,
            actor=seat,
            reason=None,
            position=_without_premove(applied, seat),
        )

    def _record(
        self,
        *,
        kind: EntryKind,
        move: Move | None,
        actor: int | None,
        reason: RejectionCode | None,
        position: Position,
    ) -> JournalEntry:
        entry = JournalEntry(kind=kind, move=move, actor=actor, reason=reason, position=position)
        self._entries.append(entry)
        return entry


def _sole_actor(position: Position) -> int | None:
    if position.state.phase == Phase.GAME_OVER:
        return None

    if len(position.state.to_act) != 1:
        return None

    return next(iter(position.state.to_act))


def _with_premove(position: Position, move: Move) -> Position:
    return position.model_copy(update={"state": position.state.with_premove(move.player, move)})


def _without_premove(position: Position, player: int) -> Position:
    return position.model_copy(update={"state": position.state.without_premove(player)})
