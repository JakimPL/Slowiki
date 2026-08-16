import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from wordcore.exceptions import NotYourTurn
from wordcore.games.game import EventView, Game
from wordcore.moves.action import ActionKind, Move, Pass
from wordcore.states.state import Phase
from wordtable.config import TimeConfig


class TableSession:
    def __init__(self, game: Game, tokens: dict[int, str], time: TimeConfig) -> None:
        self._game = game
        self._tokens = tokens
        self._time = time
        self._condition = asyncio.Condition()
        self._timer_task: asyncio.Task[None] | None = None
        self._claimed: set[int] = {0}

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

    def claim_seat(self) -> tuple[int, str] | None:
        for seat in sorted(self._tokens):
            if seat not in self._claimed:
                self._claimed.add(seat)
                return seat, self._tokens[seat]
        return None

    def view(self, observer: int | None) -> dict[str, Any]:
        return self._game.view(observer).model_dump(mode="json")

    async def submit(self, move: Move, base_seq: int, premove: bool, token: str | None) -> int:
        async with self._condition:
            observer = self.observer_for(token)
            if observer is None or observer != move.player:
                raise NotYourTurn("seat token does not match the move")
            self._game.submit(move, base_seq=base_seq, premove=premove)
            if move.action.kind != ActionKind.REORDER:
                self._schedule_timer()
            self._condition.notify_all()
            return self._game.seq

    async def events(self, observer: int | None, since: int) -> AsyncIterator[str]:
        next_seq = since
        while True:
            async with self._condition:
                pending = self._game.events(observer, since=next_seq)
                if pending:
                    next_seq = pending[-1].seq + 1
            if pending:
                for event in pending:
                    yield self._format_event(event)
                continue
            async with self._condition:
                try:
                    await asyncio.wait_for(self._condition.wait(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"

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
