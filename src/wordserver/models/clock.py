from wordcore.models.base import BaseFrozen


class ClockView(BaseFrozen):
    server_time: float
    deadline: float
    seat: int
    remaining: dict[str, float]
