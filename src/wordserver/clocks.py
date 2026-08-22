from collections.abc import Callable, Iterable
from typing import Final

from wordserver.models.clock import ClockView
from wordtable.config import TimeConfig

_LATENCY_GRACE_SECONDS: Final = 0.5


class TurnClock:
    def __init__(
        self,
        time: TimeConfig,
        seats: Iterable[int],
        now: Callable[[], float],
    ) -> None:
        self._time = time
        self._now = now
        self._remaining = _opening_budgets(time, seats)
        self._seat: int | None = None
        self._deadline: float | None = None
        self._armed_at: float | None = None
        self._version = 0

    @property
    def version(self) -> int:
        return self._version

    def armed_seat(self) -> int | None:
        return self._seat

    def arm(self, seat: int) -> float | None:
        budget = self._budget_for(seat)
        if budget is None:
            return None

        moment = self._now()
        self._seat = seat
        self._armed_at = moment
        self._deadline = moment + budget
        self._version += 1
        return budget

    def disarm(self) -> None:
        if self._deadline is None:
            return

        self._seat = None
        self._deadline = None
        self._armed_at = None
        self._version += 1

    def settle(self, *, earns_increment: bool) -> None:
        seat = self._seat
        armed_at = self._armed_at
        if seat is None or armed_at is None or seat not in self._remaining:
            return

        elapsed = max(0.0, self._now() - armed_at)
        left = max(0.0, self._remaining[seat] - elapsed)
        if earns_increment:
            left += self._time.increment_seconds
        self._remaining[seat] = left

    def spent(self, seat: int) -> bool:
        left = self._remaining.get(seat)
        return left is not None and left <= 0

    def expired(self) -> bool:
        if self._deadline is None:
            return False

        return self._now() > self._deadline + _LATENCY_GRACE_SECONDS

    def view(self) -> ClockView | None:
        if self._deadline is None or self._seat is None:
            return None

        return ClockView(
            server_time=self._now(),
            deadline=self._deadline,
            seat=self._seat,
            remaining={str(seat): left for seat, left in sorted(self._remaining.items())},
        )

    def _budget_for(self, seat: int) -> float | None:
        budgets = [
            float(seconds)
            for seconds in (self._time.per_turn_seconds, self._remaining.get(seat))
            if seconds is not None
        ]
        return min(budgets) if budgets else None


def _opening_budgets(time: TimeConfig, seats: Iterable[int]) -> dict[int, float]:
    if time.total_seconds is None:
        return {}

    return {seat: float(time.total_seconds) for seat in seats}
