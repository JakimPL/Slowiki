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


# TODO: refactor: this class contains convoluted functions
# mixes low-level and high-level responsibilities
# needs a principled approach to define concerns
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

    def events(
        self,
        observer: int | None,
        since: int,
    ) -> tuple[EventView, ...]:
        return tuple(
            event_view(
                entry,
                index,
                observer,
            )
            for index, entry in enumerate(self._entries)
            if index >= since
        )

    def submit(
        self,
        move: Move,
        base_seq: int,
        premove: bool = False,
    ) -> JournalEntry:
        position = self._require_current(base_seq)
        if premove and move.player not in position.state.to_act:
            if not self._premoves_allowed:
                raise IllegalMove("premoves are disabled at this table")

            return self._queue_premove(position, move)

        return self._play_move(position, move)

    def cancel_premove(self, player: int, base_seq: int) -> JournalEntry:
        position = self._require_current(base_seq)
        self._ensure_member(position, player)
        if position.state.premoves.get(player) is None:
            raise NoPremove("no premove is queued")

        # update state helper function should be a separate function
        new_position = position.model_copy(update={"state": position.state.without_premove(player)})
        return self._record(
            EntryKind.PREMOVE_CLEARED,
            None,
            player,
            None,
            new_position,
        )

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
        return self._record(
            EntryKind.PREMOVE_SET,
            move,
            move.player,
            None,
            new_position,
        )

    def _play_move(self, position: Position, move: Move) -> JournalEntry:
        self._ensure_member(position, move.player)
        if move.player not in position.state.to_act:
            raise NotYourTurn("player is not on turn")

        self._rules.validate(position, move)
        new_position = self._rules.apply(position, move, self._rng)
        entry = self._record(
            EntryKind.MOVE,
            move,
            move.player,
            None,
            new_position,
        )
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
        entry = JournalEntry(
            kind=kind,
            move=move,
            actor=actor,
            reason=reason,
            position=position,
        )
        self._entries.append(entry)
        return entry

    def _settle_premoves(self) -> None:
        for _ in range(len(self.position.players)):
            if not self._settle_next_premove():
                return

    # TODO: refactor
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
                EntryKind.PREMOVE_DISCARDED,
                None,
                seat,
                rejection_code(error),
                new_position,
            )
        return True
