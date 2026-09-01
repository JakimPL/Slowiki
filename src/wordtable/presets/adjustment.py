from pydantic import model_validator

from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordcore.models.letters import CategoryName, LetterValue, TileCount


class LetterAdjustment(BaseFrozen):
    value: LetterValue | None = None
    category: CategoryName | None = None
    count: TileCount | None = None

    @model_validator(mode="after")
    def _ensure_something_is_stated(self) -> "LetterAdjustment":
        if self.value is None and self.category is None and self.count is None:
            raise InvalidConfiguration("a letter adjustment states a value, a category or a count")

        return self
