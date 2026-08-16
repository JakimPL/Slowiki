from wordcore.models.base import BaseFrozen
from wordgames.names import GameName
from wordserver.session import TableSession


class TableMeta(BaseFrozen):
    scheme: str
    game: GameName
    max_players: int


class TableRegistry:
    def __init__(self) -> None:
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
