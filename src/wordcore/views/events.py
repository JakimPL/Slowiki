from wordcore.exceptions import RejectionCode
from wordcore.games.journal import EntryKind, JournalEntry
from wordcore.models.base import BaseFrozen
from wordcore.moves.action import ActionKind, Move
from wordcore.views.projection import PositionView, project


class EventView(BaseFrozen):
    seq: int
    kind: EntryKind
    actor: int | None
    move: Move | None
    reason: RejectionCode | None
    position: PositionView


def event_view(entry: JournalEntry, seq: int, observer: int | None) -> EventView:
    return EventView(
        seq=seq,
        kind=entry.kind,
        actor=entry.actor,
        move=_masked_move(entry, observer),
        reason=_masked_reason(entry, observer),
        position=project(entry.position, observer),
    )


def _masked_move(entry: JournalEntry, observer: int | None) -> Move | None:
    if entry.move is None:
        return None
    owned = observer is not None and observer == entry.actor
    match entry.kind:
        case EntryKind.MOVE:
            if entry.move.action.kind == ActionKind.REORDER and not owned:
                return None
            return entry.move
        case EntryKind.PREMOVE_SET:
            return entry.move if owned else None
        case EntryKind.PREMOVE_CLEARED | EntryKind.PREMOVE_DISCARDED:
            return None


def _masked_reason(entry: JournalEntry, observer: int | None) -> RejectionCode | None:
    if entry.reason is None:
        return None
    if observer is not None and observer == entry.actor:
        return entry.reason
    return None
