from wordcore.models.base import BaseFrozen
from wordgames.names import GameName
from wordtable.catalog import ResolvedScheme
from wordtable.config import TimeConfig


class TableMeta(BaseFrozen):
    scheme: str
    game: GameName
    max_players: int
    code: str
    resolved: ResolvedScheme
    time: TimeConfig
