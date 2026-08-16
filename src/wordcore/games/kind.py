from enum import StrEnum


class EntryKind(StrEnum):
    MOVE = "move"
    PREMOVE_SET = "premove_set"
    PREMOVE_CLEARED = "premove_cleared"
    PREMOVE_DISCARDED = "premove_discarded"
