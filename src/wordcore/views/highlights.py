from collections.abc import Callable, Iterable

from wordcore.games.journal import JournalEntry
from wordcore.games.kind import EntryKind
from wordcore.models.base import BaseFrozen
from wordcore.moves.kind import ActionKind
from wordcore.rules.score.word import ScoredWord
from wordcore.states.record import PlayRecord


class WordHighlight(BaseFrozen):
    player: int
    word: str
    points: int
    turn_number: int


class GameHighlights(BaseFrozen):
    best_word: WordHighlight | None
    longest_word: WordHighlight | None


Spoken = tuple[ScoredWord, PlayRecord]


def highlights_of(entries: Iterable[JournalEntry]) -> GameHighlights:
    spoken = tuple(_spoken(entries))
    return GameHighlights(
        best_word=_chosen(spoken, _best_rank),
        longest_word=_chosen(spoken, _longest_rank),
    )


def _spoken(entries: Iterable[JournalEntry]) -> Iterable[Spoken]:
    return ((word, record) for record in _plays(entries) for word in record.words)


def _plays(entries: Iterable[JournalEntry]) -> Iterable[PlayRecord]:
    return (record for record in map(_played, entries) if record is not None)


def _played(entry: JournalEntry) -> PlayRecord | None:
    if entry.kind != EntryKind.MOVE or entry.move is None:
        return None

    if entry.move.action.kind != ActionKind.PLAY:
        return None

    return entry.position.state.last_play


def _chosen(
    spoken: tuple[Spoken, ...], rank: Callable[[Spoken], tuple[int, int, int]]
) -> WordHighlight | None:
    chosen = max(spoken, key=rank, default=None)
    if chosen is None:
        return None

    word, record = chosen
    return WordHighlight(
        player=record.player,
        word=word.text,
        points=word.points,
        turn_number=record.turn_number,
    )


def _best_rank(spoken: Spoken) -> tuple[int, int, int]:
    word, record = spoken
    return word.points, len(word.text), -record.turn_number


def _longest_rank(spoken: Spoken) -> tuple[int, int, int]:
    word, record = spoken
    return len(word.text), word.points, -record.turn_number
