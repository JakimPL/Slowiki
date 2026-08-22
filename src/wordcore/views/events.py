from wordcore.errors.rejections import RejectionCode
from wordcore.games.journal import JournalEntry
from wordcore.games.kind import EntryKind
from wordcore.models.base import BaseFrozen
from wordcore.moves.move import Move
from wordcore.views.projection import PositionView, project


class EventView(BaseFrozen):
    seq: int
    kind: EntryKind
    actor: int | None
    move: Move | None
    reason: RejectionCode | None
    position: PositionView


def event_view(
    entry: JournalEntry,
    seq: int,
    observer: int | None,
) -> EventView:
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

    match entry.kind:
        case EntryKind.MOVE:
            return entry.move

        case EntryKind.PREMOVE_SET:
            owned = observer is not None and observer == entry.actor
            return entry.move if owned else None

        case EntryKind.PREMOVE_CLEARED | EntryKind.PREMOVE_DISCARDED:
            return None


def _masked_reason(
    entry: JournalEntry,
    observer: int | None,
) -> RejectionCode | None:
    if entry.reason is None:
        return None

    if observer is not None and observer == entry.actor:
        return entry.reason

    return None
