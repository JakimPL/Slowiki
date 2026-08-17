from wordcore.models.base import BaseFrozen


class SeatView(BaseFrozen):
    seat: int
    name: str | None
    claimed: bool
    connected: bool
