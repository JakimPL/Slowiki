from pydantic import model_validator

from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordcore.models.letters import TileCount
from wordcore.tiles.tile import LetterSpec


class TileSet(BaseFrozen):
    letters: tuple[LetterSpec, ...]
    blanks: TileCount

    @model_validator(mode="after")
    def _ensure_symbols_are_distinct(self) -> "TileSet":
        symbols = [spec.symbol for spec in self.letters]
        repeated = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
        if repeated:
            raise InvalidConfiguration(f"a tile set states {''.join(repeated)} more than once")

        return self
