from typing import Annotated, Final

from pydantic import Field, model_validator

from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordcore.models.letters import CategoryName, LetterValue, Symbols

DEFAULT_CATEGORY: Final = "standard"


class LetterClass(BaseFrozen):
    value: LetterValue
    category: CategoryName = DEFAULT_CATEGORY
    letters: Symbols


class AlphabetPreset(BaseFrozen):
    name: str
    order: Symbols
    dictionaries: Annotated[tuple[DictionaryName, ...], Field(min_length=1)]
    classes: Annotated[tuple[LetterClass, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def _ensure_the_order_is_distinct(self) -> "AlphabetPreset":
        repeated = _repeated(self.order)
        if repeated:
            raise InvalidConfiguration(f"alphabet '{self.name}' orders {repeated} more than once")

        return self

    @model_validator(mode="after")
    def _ensure_the_classes_are_disjoint(self) -> "AlphabetPreset":
        repeated = _repeated(tuple(self._classified()))
        if repeated:
            raise InvalidConfiguration(f"alphabet '{self.name}' values {repeated} more than once")

        return self

    @model_validator(mode="after")
    def _ensure_the_classes_cover_the_order(self) -> "AlphabetPreset":
        ordered = set(self.order)
        classified = set(self._classified())
        unvalued = "".join(sorted(ordered - classified))
        if unvalued:
            raise InvalidConfiguration(f"alphabet '{self.name}' gives {unvalued} no value")

        unordered = "".join(sorted(classified - ordered))
        if unordered:
            raise InvalidConfiguration(f"alphabet '{self.name}' values unordered {unordered}")

        return self

    def by_symbol(self) -> dict[str, LetterClass]:
        return {symbol: letters for letters in self.classes for symbol in letters.letters}

    def _classified(self) -> tuple[str, ...]:
        return tuple(symbol for letters in self.classes for symbol in letters.letters)


def _repeated(symbols: tuple[str, ...]) -> str:
    return "".join(sorted({symbol for symbol in symbols if symbols.count(symbol) > 1}))
