import asyncio
from collections.abc import Callable

from wordserver.fate import TableFate
from wordserver.lifetime import fate_of
from wordserver.registry import TableRegistry
from wordtable.config import TablesConfig


class TableSweep:
    def __init__(
        self,
        registry: TableRegistry,
        bounds: TablesConfig,
        now: Callable[[], float],
    ) -> None:
        self._registry = registry
        self._bounds = bounds
        self._now = now

    async def run(self) -> None:
        while True:
            await asyncio.sleep(self._bounds.sweep_seconds)
            await self.once()

    async def once(self) -> tuple[str, ...]:
        closed: list[str] = []
        for table_id, session in self._registry.tables():
            match fate_of(session.standing(), self._bounds):
                case TableFate.ABANDON:
                    await session.abandon()

                case TableFate.CLOSE:
                    await self._registry.close(table_id, at=self._now())
                    closed.append(table_id)

                case TableFate.KEEP:
                    continue

        return tuple(closed)
