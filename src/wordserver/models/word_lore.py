from lexica.lore.reading import WordLore
from wordcore.models.base import BaseFrozen


class WordLoreResponse(BaseFrozen):
    lore: dict[str, WordLore]
