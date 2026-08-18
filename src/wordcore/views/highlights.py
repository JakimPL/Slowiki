from collections.abc import Iterable

from wordcore.games.journal import JournalEntry
from wordcore.games.kind import EntryKind
from wordcore.models.base import BaseFrozen
from wordcore.moves.kind import ActionKind
from wordcore.rules.score.word import ScoredWord
from wordcore.states.record import PlayRecord


class PlayHighlight(BaseFrozen):
    player: int
    words: tuple[ScoredWord, ...]
    points: int
    turn_number: int


class WordHighlight(BaseFrozen):
    player: int
    word: str
    points: int
    turn_number: int


class GameHighlights(BaseFrozen):
    best_play: PlayHighlight | None
    longest_word: WordHighlight | None


def highlights_of(entries: Iterable[JournalEntry]) -> GameHighlights:
    plays = tuple(_plays(entries))
    return GameHighlights(
        best_play=_best_play(plays),
        longest_word=_longest_word(plays),
    )


def _plays(entries: Iterable[JournalEntry]) -> Iterable[PlayRecord]:
    return (record for record in map(_played, entries) if record is not None)


def _played(entry: JournalEntry) -> PlayRecord | None:
    if entry.kind != EntryKind.MOVE or entry.move is None:
        return None

    if entry.move.action.kind != ActionKind.PLAY:
        return None

    return entry.position.state.last_play


def _best_play(plays: tuple[PlayRecord, ...]) -> PlayHighlight | None:
    record = max(plays, key=_play_rank, default=None)
    if record is None:
        return None

    return PlayHighlight(
        player=record.player,
        words=record.words,
        points=record.points,
        turn_number=record.turn_number,
    )


def _longest_word(plays: tuple[PlayRecord, ...]) -> WordHighlight | None:
    spoken = [(word, record) for record in plays for word in record.words]
    chosen = max(spoken, key=_word_rank, default=None)
    if chosen is None:
        return None

    word, record = chosen
    return WordHighlight(
        player=record.player,
        word=word.text,
        points=word.points,
        turn_number=record.turn_number,
    )


def _play_rank(record: PlayRecord) -> tuple[int, int]:
    return record.points, -record.turn_number


def _word_rank(spoken: tuple[ScoredWord, PlayRecord]) -> tuple[int, int, int]:
    word, record = spoken
    return len(word.text), word.points, -record.turn_number
