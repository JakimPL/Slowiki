from wordcore.models.base import BaseFrozen
from wordtable.resolved import ResolvedScheme
from wordtable.timing import TimeConfig


class TableMeta(BaseFrozen):
    code: str
    resolved: ResolvedScheme
    time: TimeConfig
