from enum import StrEnum
from typing import Final


class SettingKind(StrEnum):
    TOGGLE = "toggle"
    COUNT = "count"
    OPTIONAL_COUNT = "optional_count"
    CHOICE = "choice"
    SECONDS = "seconds"
    LETTERS = "letters"


BOUNDED_KINDS: Final = frozenset(
    {
        SettingKind.COUNT,
        SettingKind.OPTIONAL_COUNT,
        SettingKind.SECONDS,
        SettingKind.LETTERS,
    }
)
OPTIONAL_KINDS: Final = frozenset({SettingKind.OPTIONAL_COUNT, SettingKind.SECONDS})
