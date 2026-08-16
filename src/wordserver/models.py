from wordcore.models.base import BaseFrozen
from wordcore.views.projection import PositionView
from wordgames.names import GameName
from wordtable.catalogue import Offering
from wordtable.config import StyleConfig


class OfferingsResponse(BaseFrozen):
    offerings: tuple[Offering, ...]


class TableAdmission(BaseFrozen):
    table_id: str
    code: str
    scheme: str
    game: GameName
    max_players: int
    seat: int
    token: str
    name: str | None


class SeatView(BaseFrozen):
    seat: int
    name: str | None
    claimed: bool
    connected: bool


class CompanyView(BaseFrozen):
    seats: tuple[SeatView, ...]


class TableViewResponse(BaseFrozen):
    seq: int
    style: StyleConfig
    view: PositionView
    company: CompanyView


class MoveAccepted(BaseFrozen):
    seq: int
