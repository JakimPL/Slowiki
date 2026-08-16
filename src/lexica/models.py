from enum import StrEnum

from wordcore.models.base import BaseFrozen


class EntryStatus(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class WordEntry(BaseFrozen):
    surface: str
    base_form: str | None = None
    homonym_id: int | None = None
    categories: frozenset[str] = frozenset()
    variants: tuple[str, ...] = ()
    status: EntryStatus = EntryStatus.ENABLED
    source: str = "unknown"


def entry_from_word(word: str, source: str) -> WordEntry:
    return WordEntry(surface=word, source=source)
