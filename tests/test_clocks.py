from wordserver.clocks import TurnClock
from wordtable.config import TimeConfig


class _FakeClock:
    def __init__(self) -> None:
        self.moment = 100.0

    def __call__(self) -> float:
        return self.moment


def _clock(time: TimeConfig, moment: _FakeClock) -> TurnClock:
    return TurnClock(time, (0, 1), moment)


def test_per_turn_budget_repeats_every_turn() -> None:
    moment = _FakeClock()
    clock = _clock(TimeConfig(per_turn_seconds=90, increment_seconds=0, total_seconds=None), moment)
    assert clock.arm(0) == 90.0
    moment.moment = 150.0
    clock.settle(earns_increment=True)
    assert clock.arm(1) == 90.0
    view = clock.view()
    assert view is not None
    assert view.seat == 1
    assert view.deadline == 240.0
    assert view.remaining == {}


def test_total_budget_charges_thinking_time_and_pays_the_increment() -> None:
    moment = _FakeClock()
    clock = _clock(
        TimeConfig(per_turn_seconds=None, increment_seconds=10, total_seconds=300), moment
    )
    assert clock.arm(0) == 300.0
    moment.moment = 140.0
    clock.settle(earns_increment=True)
    assert clock.arm(1) == 300.0
    moment.moment = 160.0
    clock.settle(earns_increment=False)
    assert clock.arm(0) == 270.0
    view = clock.view()
    assert view is not None
    assert view.remaining == {"0": 270.0, "1": 280.0}


def test_the_shorter_of_the_two_budgets_bounds_a_turn() -> None:
    moment = _FakeClock()
    clock = _clock(TimeConfig(per_turn_seconds=60, increment_seconds=0, total_seconds=100), moment)
    assert clock.arm(0) == 60.0
    moment.moment = 150.0
    clock.settle(earns_increment=False)
    assert clock.arm(0) == 50.0


def test_a_spent_budget_flags_its_seat() -> None:
    moment = _FakeClock()
    clock = _clock(TimeConfig(per_turn_seconds=None, increment_seconds=0, total_seconds=30), moment)
    clock.arm(0)
    moment.moment = 200.0
    clock.settle(earns_increment=False)
    assert clock.flagged(0) is True
    assert clock.flagged(1) is False
    assert clock.all_flagged() is False
    clock.arm(1)
    moment.moment = 400.0
    clock.settle(earns_increment=False)
    assert clock.all_flagged() is True


def test_disarming_hides_the_clock_and_moves_the_version() -> None:
    moment = _FakeClock()
    clock = _clock(TimeConfig(per_turn_seconds=90, increment_seconds=0, total_seconds=None), moment)
    assert clock.view() is None
    clock.arm(0)
    armed = clock.version
    assert clock.armed_seat() == 0
    clock.disarm()
    assert clock.view() is None
    assert clock.version > armed
    assert clock.armed_seat() is None


def test_an_untimed_table_never_arms() -> None:
    moment = _FakeClock()
    clock = _clock(
        TimeConfig(per_turn_seconds=None, increment_seconds=0, total_seconds=None), moment
    )
    assert clock.arm(0) is None
    assert clock.view() is None
    assert clock.flagged(0) is False
    assert clock.all_flagged() is False
