from typing import NamedTuple

from wordserver.fate import TableFate
from wordtable.config import TablesConfig


class TableStanding(NamedTuple):
    age: float
    finished_for: float | None


def fate_of(standing: TableStanding, bounds: TablesConfig) -> TableFate:
    if standing.finished_for is not None:
        return _read_enough(standing.finished_for, bounds)

    if standing.age >= bounds.life_seconds:
        return TableFate.ABANDON

    return TableFate.KEEP


def _read_enough(finished_for: float, bounds: TablesConfig) -> TableFate:
    if finished_for >= bounds.linger_seconds:
        return TableFate.CLOSE

    return TableFate.KEEP
