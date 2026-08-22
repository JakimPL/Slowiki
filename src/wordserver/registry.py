import logging

from wordserver.models.game_record import GameRecord
from wordserver.models.table_meta import TableMeta
from wordserver.records import GameBook, game_record
from wordserver.session import TableSession

logger = logging.getLogger(__name__)


class TableRegistry:
    def __init__(self, book: GameBook) -> None:
        self._book = book
        self._tables: dict[str, TableSession] = {}
        self._codes: dict[str, str] = {}
        self._meta: dict[str, TableMeta] = {}

    def add(self, table_id: str, session: TableSession, meta: TableMeta) -> None:
        self._tables[table_id] = session
        self._meta[table_id] = meta

    def add_code(self, code: str, table_id: str) -> None:
        self._codes[code] = table_id

    def get(self, table_id: str) -> TableSession | None:
        return self._tables.get(table_id)

    def table_id_for_code(self, code: str) -> str | None:
        return self._codes.get(code)

    def meta_for(self, table_id: str) -> TableMeta | None:
        return self._meta.get(table_id)

    def tables(self) -> tuple[tuple[str, TableSession], ...]:
        return tuple(self._tables.items())

    def record_for(self, table_id: str) -> GameRecord | None:
        return self._book.record_for(table_id)

    async def close(self, table_id: str, at: float) -> GameRecord | None:
        session = self._tables.get(table_id)
        meta = self._meta.get(table_id)
        if session is None or meta is None:
            return None

        record = game_record(table_id, meta, session, closed=at)
        self._book.remember(record)
        del self._tables[table_id]
        del self._meta[table_id]
        self._codes.pop(meta.code, None)
        await session.close()
        logger.info("table closed: %s", record.model_dump_json())
        return record
