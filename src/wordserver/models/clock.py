from wordcore.models.base import BaseFrozen


class ClockView(BaseFrozen):
    server_time: float
    deadline: float
    seat: int
    per_turn_seconds: int
