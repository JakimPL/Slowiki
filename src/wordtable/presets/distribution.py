from typing import Annotated

from pydantic import Field, model_validator

from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordcore.models.letters import Symbols, TileCount


class DistributionPreset(BaseFrozen):
    name: str
    counts: Annotated[dict[TileCount, Symbols], Field(min_length=1)]

    @model_validator(mode="after")
    def _ensure_symbols_are_counted_once(self) -> "DistributionPreset":
        counted = tuple(self._counted())
        repeated = "".join(sorted({symbol for symbol in counted if counted.count(symbol) > 1}))
        if repeated:
            raise InvalidConfiguration(
                f"distribution '{self.name}' counts {repeated} more than once"
            )

        return self

    def by_symbol(self) -> dict[str, int]:
        return {symbol: count for count, symbols in self.counts.items() for symbol in symbols}

    def _counted(self) -> tuple[str, ...]:
        return tuple(symbol for symbols in self.counts.values() for symbol in symbols)
