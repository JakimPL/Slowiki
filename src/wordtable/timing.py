from wordcore.models.base import BaseFrozen
from wordtable.rules import RulesConfig


class TimeConfig(BaseFrozen):
    per_turn_seconds: int | None
    increment_seconds: int
    total_seconds: int | None


def time_of(rules: RulesConfig) -> TimeConfig:
    return TimeConfig(
        per_turn_seconds=rules.per_turn_seconds,
        increment_seconds=rules.increment_seconds,
        total_seconds=rules.total_seconds,
    )
