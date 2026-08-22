from wordcore.models.base import BaseFrozen
from wordcore.states.phase import Phase
from wordgames.names import GameName


class SeatRecord(BaseFrozen):
    seat: int
    name: str | None
    score: int


class GameRecord(BaseFrozen):
    table_id: str
    scheme: str
    game: GameName
    phase: Phase
    seats: tuple[SeatRecord, ...]
    turns: int
    opened: float
    closed: float
