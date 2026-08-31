import asyncio
import json
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Final

from wordcore.errors.rejections import RejectionCode
from wordcore.games.game import Game
from wordcore.models.base import BaseFrozen
from wordcore.moves.action import Pass
from wordcore.moves.kind import ActionKind
from wordcore.moves.move import Move
from wordcore.rules.rack import rack_of
from wordcore.states.phase import finished
from wordcore.views.events import EventView
from wordcore.views.highlights import GameHighlights
from wordcore.views.projection import PositionView
from wordserver.clocks import TurnClock
from wordserver.errors.exceptions import (
    OutOfTime,
    RackMismatch,
    SeatTokenMismatch,
    TableGathering,
)
from wordserver.lifetime import TableStanding
from wordserver.models.clock import ClockView
from wordserver.models.company import CompanyView
from wordserver.models.heartbeat import HeartbeatView
from wordserver.models.seat import SeatView
from wordserver.racks import RackOrder
from wordtable.timing import TimeConfig

_HEARTBEAT_SECONDS: Final = 15
_PRESENCE_EVENT: Final = "presence"
_HEARTBEAT_EVENT: Final = "heartbeat"
_POSITION_EVENT: Final = "position"
_CLOCK_EVENT: Final = "clock"


@dataclass
class _StreamCursor:
    next_seq: int
    seen_company: int
    seen_view: int
    seen_clock: int


class TableSession:
    def __init__(
        self,
        game: Game,
        tokens: dict[int, str],
        time: TimeConfig,
        names: dict[int, str | None],
        now: Callable[[], float],
        *,
        premove_delay_seconds: float,
    ) -> None:
        self._game = game
        self._tokens = tokens
        self._names = names
        self._now = now
        self._time = time
        self._premove_delay_seconds = premove_delay_seconds
        self._clock = TurnClock(time, tokens, now)
        self._racks = RackOrder(tokens)
        self._condition = asyncio.Condition()
        self._timer_task: asyncio.Task[None] | None = None
        self._premove_task: asyncio.Task[None] | None = None
        self._claimed: set[int] = {0}
        self._streams: dict[int, int] = {}
        self._company_version = 0
        self._view_version = 0
        self._opened = now()
        self._finished_at: float | None = None
        self._closed = False
        if not self.gathering():
            self._schedule_timer()

    @property
    def seq(self) -> int:
        return self._game.seq

    @property
    def opened(self) -> float:
        return self._opened

    def standing(self) -> TableStanding:
        moment = self._now()
        return TableStanding(
            age=moment - self._opened,
            finished_for=None if self._finished_at is None else moment - self._finished_at,
        )

    async def close(self) -> None:
        self._cancel_timer()
        self._cancel_premove_timer()
        async with self._condition:
            self._closed = True
            self._condition.notify_all()

    async def abandon(self) -> None:
        async with self._condition:
            if not self._running():
                return

            self._game.abandon()
            self._schedule_timer()
            self._cancel_premove_timer()
            self._stirred()

    def observer_for(self, token: str | None) -> int | None:
        if token is None:
            return None

        for seat, seat_token in self._tokens.items():
            if seat_token == token:
                return seat

        return None

    async def claim(self, name: str | None) -> tuple[int, str] | None:
        async with self._condition:
            for seat in sorted(self._tokens):
                if seat not in self._claimed:
                    self._seat_taken(seat, name)
                    self._stirred()
                    return seat, self._tokens[seat]

            return None

    def company(self) -> CompanyView:
        return CompanyView(
            seats=tuple(
                SeatView(
                    seat=seat,
                    name=self._names.get(seat),
                    claimed=seat in self._claimed,
                    connected=self._streams.get(seat, 0) > 0,
                )
                for seat in sorted(self._tokens)
            )
        )

    def gathering(self) -> bool:
        return len(self._claimed) < len(self._tokens)

    def view(self, observer: int | None) -> PositionView:
        if self.gathering():
            return self._game.view(None)

        return self._racks.arranged(self._game.view(observer), observer)

    def highlights(self) -> GameHighlights:
        return self._game.highlights()

    def clock(self) -> ClockView | None:
        return self._clock.view()

    async def submit(
        self,
        move: Move,
        *,
        base_seq: int,
        premove: bool,
        token: str | None,
    ) -> int:
        async with self._condition:
            observer = self.observer_for(token)
            if observer is None or observer != move.player:
                raise SeatTokenMismatch("seat token does not match the move")

            self._ensure_gathered()
            self._ensure_in_time(move.player)
            before = self._turn_cursor()
            self._game.submit(move, base_seq=base_seq, premove=premove)
            if self._turn_cursor() != before:
                self._turn_opened(move)

            self._stirred()
            return self._game.seq

    async def arrange_rack(self, tile_ids: tuple[int, ...], *, token: str | None) -> None:
        async with self._condition:
            observer = self.observer_for(token)
            if observer is None:
                raise SeatTokenMismatch("seat token does not match a seat")

            self._ensure_whole_rack(observer, tile_ids)
            self._racks.remember(observer, tile_ids)

    async def cancel_premove(self, base_seq: int, *, token: str | None) -> int:
        async with self._condition:
            observer = self.observer_for(token)
            if observer is None:
                raise SeatTokenMismatch("seat token does not match a seat")

            self._ensure_gathered()
            self._game.cancel_premove(observer, base_seq)
            self._stirred()
            return self._game.seq

    def _seat_taken(self, seat: int, name: str | None) -> None:
        self._claimed.add(seat)
        self._names[seat] = name
        self._company_version += 1
        if self.gathering():
            return

        self._view_version += 1
        self._schedule_timer()

    def _ensure_whole_rack(self, seat: int, tile_ids: tuple[int, ...]) -> None:
        held = sorted(tile.identifier for tile in rack_of(self._game.position, seat))
        if sorted(tile_ids) != held:
            raise RackMismatch("the rack order must list every rack tile exactly once")

    def _ensure_gathered(self) -> None:
        if self.gathering():
            raise TableGathering("the table is still gathering players")

    def _ensure_in_time(self, seat: int) -> None:
        if self._out_of_time(seat):
            raise OutOfTime("the seat has run out of time")

    def _out_of_time(self, seat: int) -> bool:
        if self._clock.spent(seat):
            return True

        return seat == self._clock.armed_seat() and self._clock.expired()

    def _turn_cursor(self) -> tuple[frozenset[int], int]:
        state = self._game.position.state
        return state.to_act, state.turn_number

    async def events(
        self,
        observer: int | None,
        since: int,
    ) -> AsyncIterator[str]:
        self._count_stream(observer, 1)
        await asyncio.shield(self._announce())
        try:
            cursor = _StreamCursor(
                next_seq=since,
                seen_company=-1,
                seen_view=-1,
                seen_clock=-1,
            )
            while not self._closed:
                for frame in await self._next_frames(observer, cursor):
                    yield frame

        finally:
            self._count_stream(observer, -1)
            await asyncio.shield(self._announce())

    async def _next_frames(
        self,
        observer: int | None,
        cursor: _StreamCursor,
    ) -> list[str]:
        async with self._condition:
            while not self._closed:
                frames = self._pending_frames(observer, cursor)
                if frames:
                    return frames

                if await self._quiet_through_heartbeat():
                    return [_named_frame(_HEARTBEAT_EVENT, self._heartbeat())]

            return []

    def _pending_frames(
        self,
        observer: int | None,
        cursor: _StreamCursor,
    ) -> list[str]:
        frames: list[str] = []
        if cursor.seen_company != self._company_version:
            cursor.seen_company = self._company_version
            frames.append(_named_frame(_PRESENCE_EVENT, self.company()))

        if cursor.seen_view != self._view_version:
            cursor.seen_view = self._view_version
            frames.append(_named_frame(_POSITION_EVENT, self.view(observer)))

        if cursor.seen_clock != self._clock.version:
            cursor.seen_clock = self._clock.version
            clock = self.clock()
            if clock is not None:
                frames.append(_named_frame(_CLOCK_EVENT, clock))

        for event in self._game.events(observer, since=cursor.next_seq):
            cursor.next_seq = event.seq + 1
            frames.append(_numbered_frame(self._arranged_event(event, observer)))

        return frames

    def _arranged_event(self, event: EventView, observer: int | None) -> EventView:
        return event.model_copy(
            update={"position": self._racks.arranged(event.position, observer)},
        )

    async def _quiet_through_heartbeat(self) -> bool:
        try:
            await asyncio.wait_for(
                self._condition.wait(),
                timeout=_HEARTBEAT_SECONDS,
            )
        except TimeoutError:
            return True

        return False

    def _heartbeat(self) -> HeartbeatView:
        return HeartbeatView(server_time=self._now())

    def _count_stream(self, observer: int | None, delta: int) -> None:
        if observer is None:
            return

        self._streams[observer] = self._streams.get(observer, 0) + delta
        self._company_version += 1

    async def _announce(self) -> None:
        async with self._condition:
            self._condition.notify_all()

    def _stirred(self) -> None:
        if self._finished_at is None and not self._running():
            self._finished_at = self._now()

        self._condition.notify_all()

    def _running(self) -> bool:
        return not finished(self._game.position.state.phase)

    def _turn_opened(self, move: Move | None) -> None:
        self._clock.settle(earns_increment=self._earns_increment(move))
        self._schedule_timer()
        self._schedule_premove()

    def _earns_increment(self, move: Move | None) -> bool:
        if move is None or move.player != self._clock.armed_seat():
            return False

        return move.action.kind in (ActionKind.PLAY, ActionKind.EXCHANGE)

    def _discard_premove(self, seat: int, reason: RejectionCode) -> None:
        if self._game.position.state.premoves.get(seat) is None:
            return

        self._game.discard_premove(seat, self._game.seq, reason)

    def _cancel_timer(self) -> None:
        if self._timer_task is not None:
            self._timer_task.cancel()
            self._timer_task = None

    def _schedule_timer(self) -> None:
        self._cancel_timer()
        seat = self._sole_actor()
        if seat is None:
            self._clock.disarm()
            return

        budget = self._clock.arm(seat)
        if budget is None:
            return

        self._timer_task = asyncio.create_task(self._timeout(seat, budget))

    def _cancel_premove_timer(self) -> None:
        if self._premove_task is not None:
            self._premove_task.cancel()
            self._premove_task = None

    def _schedule_premove(self) -> None:
        self._cancel_premove_timer()
        seat = self._premoving_seat()
        if seat is None:
            return

        self._premove_task = asyncio.create_task(self._settle_premove(seat))

    def _sole_actor(self) -> int | None:
        state = self._game.position.state
        if finished(state.phase) or len(state.to_act) != 1:
            return None

        return next(iter(state.to_act))

    def _premoving_seat(self) -> int | None:
        seat = self._sole_actor()
        if seat is None or self._game.position.state.premoves.get(seat) is None:
            return None

        return seat

    async def _settle_premove(self, seat: int) -> None:
        await asyncio.sleep(self._premove_delay_seconds)
        async with self._condition:
            if self._premoving_seat() != seat:
                return

            before = self._turn_cursor()
            settled = self._premove_answer(seat)
            if self._turn_cursor() != before:
                self._turn_opened(settled)

            self._stirred()

    def _premove_answer(self, seat: int) -> Move | None:
        if self._out_of_time(seat):
            self._discard_premove(seat, RejectionCode.OUT_OF_TIME)
            return None

        settled = self._game.settle_premove()
        return settled.move if settled is not None else None

    async def _timeout(self, seat: int, seconds: float) -> None:
        await asyncio.sleep(seconds)
        async with self._condition:
            position = self._game.position
            if finished(position.state.phase):
                return

            if position.state.to_act != frozenset({seat}):
                return

            self._clock.settle(earns_increment=False)
            self._discard_premove(seat, RejectionCode.OUT_OF_TIME)
            self._game.submit(
                Move(player=seat, action=Pass()),
                base_seq=self._game.seq,
            )
            self._schedule_timer()
            self._schedule_premove()
            self._stirred()


def _numbered_frame(event: EventView) -> str:
    return f"id: {event.seq}\ndata: {_payload(event)}\n\n"


def _named_frame(name: str, view: BaseFrozen) -> str:
    return f"event: {name}\ndata: {_payload(view)}\n\n"


def _payload(view: BaseFrozen) -> str:
    return json.dumps(view.model_dump(mode="json"))
