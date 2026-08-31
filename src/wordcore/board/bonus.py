from enum import StrEnum

from wordcore.models.base import BaseFrozen
from wordcore.models.letters import CategoryName


class BonusKind(StrEnum):
    WORD_MULTIPLIER = "word_multiplier"
    LETTER_MULTIPLIER = "letter_multiplier"
    CATEGORY_MULTIPLIER = "category_multiplier"


class Bonus(BaseFrozen):
    kind: BonusKind
    multiplier: int
    category: CategoryName | None = None
