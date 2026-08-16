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


class TableViewResponse(BaseFrozen):
    seq: int
    style: StyleConfig
    view: PositionView


class MoveAccepted(BaseFrozen):
    seq: int
