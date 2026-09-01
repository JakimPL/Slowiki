from collections import deque
from typing import Final

from wordserver.models.game_record import GameRecord, SeatRecord
from wordserver.models.table_meta import TableMeta
from wordserver.session import TableSession

KEPT_GAMES: Final = 256


def game_record(
    table_id: str,
    meta: TableMeta,
    session: TableSession,
    closed: float,
) -> GameRecord:
    view = session.view(None)
    return GameRecord(
        table_id=table_id,
        scheme=meta.resolved.scheme,
        rules=meta.resolved.rules,
        phase=view.phase,
        seats=tuple(
            SeatRecord(
                seat=seated.seat,
                name=seated.name,
                score=view.scores.get(seated.seat, 0),
            )
            for seated in session.company().seats
        ),
        turns=view.turn_number,
        opened=session.opened,
        closed=closed,
    )


class GameBook:
    def __init__(self, kept: int) -> None:
        self._kept = kept
        self._records: dict[str, GameRecord] = {}
        self._order: deque[str] = deque()

    def remember(self, record: GameRecord) -> None:
        self._records[record.table_id] = record
        self._order.append(record.table_id)
        while len(self._order) > self._kept:
            self._records.pop(self._order.popleft(), None)

    def record_for(self, table_id: str) -> GameRecord | None:
        return self._records.get(table_id)
