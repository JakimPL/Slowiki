from enum import StrEnum

from wordcore.exceptions import RejectionCode
from wordcore.models.base import BaseFrozen
from wordcore.moves.action import Move
from wordcore.positions.position import Position


class EntryKind(StrEnum):
    MOVE = "move"
    PREMOVE_SET = "premove_set"
    PREMOVE_CLEARED = "premove_cleared"
    PREMOVE_DISCARDED = "premove_discarded"


class JournalEntry(BaseFrozen):
    kind: EntryKind
    move: Move | None
    actor: int | None
    reason: RejectionCode | None
    position: Position
