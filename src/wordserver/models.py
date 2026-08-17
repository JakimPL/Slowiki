from lexica.names import DictionaryName
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Letter
from wordcore.views.projection import PositionView
from wordgames.names import GameName
from wordtable.catalogue import Offering
from wordtable.config import TimeConfig


class OfferingsResponse(BaseFrozen):
    offerings: tuple[Offering, ...]


class RuleParameters(BaseFrozen):
    rack_size: int | None
    exchange_limit: int | None
    exchange_min_bag: int
    pass_allowed: bool
    bingo_bonus: int
    validate_on_play: bool
    premoves_allowed: bool
    pass_end_limit: int | None
    scoreless_end_limit: int | None
    time: TimeConfig


class TableDescription(BaseFrozen):
    code: str | None
    scheme: str
    game: GameName
    seats: int
    dictionary: DictionaryName
    parameters: RuleParameters
    alphabet: tuple[Letter, ...]
    distribution: dict[str, int]
    blanks: int


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


class ClockView(BaseFrozen):
    server_time: float
    deadline: float
    seat: int
    per_turn_seconds: int


class TableViewResponse(BaseFrozen):
    seq: int
    view: PositionView
    company: CompanyView
    clock: ClockView | None


class MoveAccepted(BaseFrozen):
    seq: int
