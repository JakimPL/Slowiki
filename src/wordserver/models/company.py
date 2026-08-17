from wordcore.models.base import BaseFrozen
from wordserver.models.seat import SeatView


class CompanyView(BaseFrozen):
    seats: tuple[SeatView, ...]
