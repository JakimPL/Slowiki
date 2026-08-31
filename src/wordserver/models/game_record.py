from wordcore.models.base import BaseFrozen
from wordcore.states.phase import Phase
from wordtable.names import PresetName
from wordtable.rules import RulesConfig


class SeatRecord(BaseFrozen):
    seat: int
    name: str | None
    score: int


class GameRecord(BaseFrozen):
    table_id: str
    scheme: PresetName
    rules: RulesConfig
    phase: Phase
    seats: tuple[SeatRecord, ...]
    turns: int
    opened: float
    closed: float
