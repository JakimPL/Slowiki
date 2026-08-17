from wordcore.models.base import BaseFrozen
from wordcore.views.projection import PositionView
from wordserver.models.clock import ClockView
from wordserver.models.company import CompanyView


class TableViewResponse(BaseFrozen):
    seq: int
    view: PositionView
    company: CompanyView
    clock: ClockView | None
