from enum import StrEnum


class SettingKind(StrEnum):
    TOGGLE = "toggle"
    COUNT = "count"
    OPTIONAL_COUNT = "optional_count"
    CHOICE = "choice"
    SECONDS = "seconds"
    LETTERS = "letters"
