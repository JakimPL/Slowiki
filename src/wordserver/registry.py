from wordserver.session import TableSession


class TableRegistry:
    def __init__(self) -> None:
        self._tables: dict[str, TableSession] = {}

    def add(self, table_id: str, session: TableSession) -> None:
        self._tables[table_id] = session

    def get(self, table_id: str) -> TableSession | None:
        return self._tables.get(table_id)
