import asyncio
import json
from collections.abc import AsyncIterator
from typing import Final

from wordcore.games.game import Game
from wordcore.moves.action import ActionKind, Move, Pass
from wordcore.states.state import Phase
from wordcore.views.events import EventView
from wordcore.views.projection import PositionView
from wordserver.errors import SeatTokenMismatch
from wordserver.models import CompanyView, SeatView
from wordtable.config import TimeConfig

_KEEPALIVE_SECONDS: Final = 15


class TableSession:
    def __init__(
        self,
        game: Game,
        tokens: dict[int, str],
        time: TimeConfig,
        names: dict[int, str | None],
    ) -> None:
        self._game = game
        self._tokens = tokens
        self._time = time
        self._names = names
        self._condition = asyncio.Condition()
        self._timer_task: asyncio.Task[None] | None = None
        self._claimed: set[int] = {0}
        self._streams: dict[int, int] = {}
        self._company_version = 0

    @property
    def seq(self) -> int:
        return self._game.seq

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

    def view(self, observer: int | None) -> PositionView:
        return self._game.view(observer)

    async def submit(self, move: Move, base_seq: int, premove: bool, token: str | None) -> int:
        async with self._condition:
            observer = self.observer_for(token)
            if observer is None or observer != move.player:
                raise SeatTokenMismatch("seat token does not match the move")
            self._game.submit(move, base_seq=base_seq, premove=premove)
            if move.action.kind != ActionKind.REORDER:
                self._schedule_timer()
            self._condition.notify_all()
            return self._game.seq

    async def cancel_premove(self, base_seq: int, token: str | None) -> int:
        async with self._condition:
            observer = self.observer_for(token)
            if observer is None:
                raise SeatTokenMismatch("seat token does not match a seat")
            self._game.cancel_premove(observer, base_seq)
            self._condition.notify_all()
            return self._game.seq

    async def events(self, observer: int | None, since: int) -> AsyncIterator[str]:
        await self._open_stream(observer)
        try:
            next_seq = since
            seen_version = -1
            while True:
                async with self._condition:
                    pending = self._game.events(observer, since=next_seq)
                    if pending:
                        next_seq = pending[-1].seq + 1
                    version = self._company_version
                    company = self.company() if version != seen_version else None
                if company is not None or pending:
                    if company is not None:
                        seen_version = version
                        yield _format_presence(company)
                    for event in pending:
                        yield self._format_event(event)
                    continue
                async with self._condition:
                    try:
                        await asyncio.wait_for(self._condition.wait(), timeout=_KEEPALIVE_SECONDS)
                    except asyncio.TimeoutError:
                        yield ": keepalive\n\n"
        finally:
            await self._close_stream(observer)

    async def _open_stream(self, observer: int | None) -> None:
        if observer is None:
            return
        async with self._condition:
            self._streams[observer] = self._streams.get(observer, 0) + 1
            self._company_version += 1
            self._condition.notify_all()

    async def _close_stream(self, observer: int | None) -> None:
        if observer is None:
            return
        async with self._condition:
            self._streams[observer] = self._streams.get(observer, 1) - 1
            self._company_version += 1
            self._condition.notify_all()

    def _format_event(self, event: EventView) -> str:
        payload = json.dumps(event.model_dump(mode="json"))
        return f"id: {event.seq}\ndata: {payload}\n\n"

    def _schedule_timer(self) -> None:
        if self._timer_task is not None:
            self._timer_task.cancel()
            self._timer_task = None
        position = self._game.position
        if position.state.phase == Phase.GAME_OVER or len(position.state.to_act) != 1:
            return
        seat = next(iter(position.state.to_act))
        seconds = self._time.per_turn_seconds
        if seconds is None:
            return
        self._timer_task = asyncio.create_task(self._timeout(seat, seconds))

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


def _format_presence(company: CompanyView) -> str:
    payload = json.dumps(company.model_dump(mode="json"))
    return f"event: presence\ndata: {payload}\n\n"
