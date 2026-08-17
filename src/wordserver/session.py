import asyncio
import json
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Final

from wordcore.games.game import Game
from wordcore.moves.action import Pass
from wordcore.moves.move import Move
from wordcore.states.state import Phase
from wordcore.views.events import EventView
from wordcore.views.projection import PositionView
from wordserver.errors import SeatTokenMismatch, TableGathering
from wordserver.models import ClockView, CompanyView, SeatView
from wordtable.config import TimeConfig

_KEEPALIVE_SECONDS: Final = 15
_KEEPALIVE_FRAME: Final = ": keepalive\n\n"


@dataclass
class _StreamCursor:
    next_seq: int
    seen_company: int
    seen_clock: int


class TableSession:
    def __init__(
        self,
        game: Game,
        tokens: dict[int, str],
        time: TimeConfig,
        names: dict[int, str | None],
        now: Callable[[], float],
    ) -> None:
        self._game = game
        self._tokens = tokens
        self._time = time
        self._names = names
        self._now = now
        self._condition = asyncio.Condition()
        self._timer_task: asyncio.Task[None] | None = None
        self._claimed: set[int] = {0}
        self._streams: dict[int, int] = {}
        self._company_version = 0
        self._deadline: float | None = None
        self._deadline_seat: int | None = None
        self._clock_version = 0
        if not self.gathering():
            self._schedule_timer()

    @property
    def seq(self) -> int:
        return self._game.seq

    def close(self) -> None:
        if self._timer_task is not None:
            self._timer_task.cancel()
            self._timer_task = None

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
                    self._claimed.add(seat)
                    self._names[seat] = name
                    self._company_version += 1
                    if not self.gathering():
                        self._schedule_timer()

                    self._condition.notify_all()
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

        return self._game.view(observer)

    def clock(self) -> ClockView | None:
        seconds = self._time.per_turn_seconds
        if self._deadline is None or self._deadline_seat is None or seconds is None:
            return None

        return ClockView(
            server_time=self._now(),
            deadline=self._deadline,
            seat=self._deadline_seat,
            per_turn_seconds=seconds,
        )

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
            before = self._turn_cursor()
            self._game.submit(move, base_seq=base_seq, premove=premove)
            if self._turn_cursor() != before:
                self._schedule_timer()

            self._condition.notify_all()
            return self._game.seq

    async def cancel_premove(self, base_seq: int, *, token: str | None) -> int:
        async with self._condition:
            observer = self.observer_for(token)
            if observer is None:
                raise SeatTokenMismatch("seat token does not match a seat")

            self._ensure_gathered()
            self._game.cancel_premove(observer, base_seq)
            self._condition.notify_all()
            return self._game.seq

    def _ensure_gathered(self) -> None:
        if self.gathering():
            raise TableGathering("the table is still gathering players")

    def _turn_cursor(self) -> tuple[frozenset[int], int]:
        state = self._game.position.state
        return state.to_act, state.turn_number

    async def events(self, observer: int | None, since: int) -> AsyncIterator[str]:
        await self._adjust_streams(observer, 1)
        try:
            cursor = _StreamCursor(next_seq=since, seen_company=-1, seen_clock=-1)
            while True:
                frames = await self._fresh_frames(observer, cursor)
                for frame in frames:
                    yield frame

                if frames:
                    continue

                if await self._timed_out_waiting():
                    yield _KEEPALIVE_FRAME

        finally:
            await self._adjust_streams(observer, -1)

    async def _fresh_frames(self, observer: int | None, cursor: _StreamCursor) -> list[str]:
        async with self._condition:
            frames: list[str] = []
            if cursor.seen_company != self._company_version:
                cursor.seen_company = self._company_version
                frames.append(_format_presence(self.company()))

            if cursor.seen_clock != self._clock_version:
                cursor.seen_clock = self._clock_version
                clock = self.clock()
                if clock is not None:
                    frames.append(_format_clock(clock))

            for event in self._game.events(observer, since=cursor.next_seq):
                cursor.next_seq = event.seq + 1
                frames.append(_format_event(event))

            return frames

    async def _timed_out_waiting(self) -> bool:
        async with self._condition:
            try:
                await asyncio.wait_for(self._condition.wait(), timeout=_KEEPALIVE_SECONDS)
            except TimeoutError:
                return True

            return False

    async def _adjust_streams(self, observer: int | None, delta: int) -> None:
        if observer is None:
            return

        async with self._condition:
            self._streams[observer] = self._streams.get(observer, 0) + delta
            self._company_version += 1
            self._condition.notify_all()

    def _schedule_timer(self) -> None:
        if self._timer_task is not None:
            self._timer_task.cancel()
            self._timer_task = None

        position = self._game.position
        seconds = self._time.per_turn_seconds
        if seconds is None:
            return

        if position.state.phase == Phase.GAME_OVER or len(position.state.to_act) != 1:
            self._clear_deadline()
            return

        seat = next(iter(position.state.to_act))
        self._deadline = self._now() + seconds
        self._deadline_seat = seat
        self._clock_version += 1
        self._timer_task = asyncio.create_task(self._timeout(seat, seconds))

    def _clear_deadline(self) -> None:
        if self._deadline is not None:
            self._deadline = None
            self._deadline_seat = None
            self._clock_version += 1

    async def _timeout(self, seat: int, seconds: int) -> None:
        await asyncio.sleep(seconds)
        async with self._condition:
            position = self._game.position
            if position.state.phase == Phase.GAME_OVER:
                return

            if position.state.to_act != frozenset({seat}):
                return

            self._game.submit(Move(player=seat, action=Pass()), base_seq=self._game.seq)
            self._schedule_timer()
            self._condition.notify_all()


def _format_event(event: EventView) -> str:
    payload = json.dumps(event.model_dump(mode="json"))
    return f"id: {event.seq}\ndata: {payload}\n\n"


def _format_presence(company: CompanyView) -> str:
    payload = json.dumps(company.model_dump(mode="json"))
    return f"event: presence\ndata: {payload}\n\n"


def _format_clock(clock: ClockView) -> str:
    payload = json.dumps(clock.model_dump(mode="json"))
    return f"event: clock\ndata: {payload}\n\n"
