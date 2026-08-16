from wordcore.exceptions import RejectionCode
from wordcore.games.kind import EntryKind
from wordcore.models.base import BaseFrozen
from wordcore.moves.move import Move
from wordcore.positions.position import Position


class JournalEntry(BaseFrozen):
    kind: EntryKind
    move: Move | None
    actor: int | None
    reason: RejectionCode | None
    position: Position
