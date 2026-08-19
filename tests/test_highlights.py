from wordcore.board.board import Board
from wordcore.games.journal import JournalEntry
from wordcore.games.kind import EntryKind
from wordcore.moves.action import Exchange, Pass, Play, PlayPlacement
from wordcore.moves.move import Move
from wordcore.positions.position import Position
from wordcore.rules.score.word import ScoredWord
from wordcore.states.record import PlayRecord
from wordcore.states.state import Phase, WordState
from wordcore.views.highlights import highlights_of

LAID = Play(placements=(PlayPlacement(tile_id=1, row=0, column=0),))


def make_record(
    player: int,
    words: tuple[tuple[str, int], ...],
    points: int,
    turn_number: int,
) -> PlayRecord:
    return PlayRecord(
        player=player,
        indices=(0,),
        words=tuple(ScoredWord(text=text, points=scored) for text, scored in words),
        points=points,
        bingo=0,
        turn_number=turn_number,
    )


def make_position(record: PlayRecord | None) -> Position:
    state = WordState(
        phase=Phase.TURN,
        to_act=frozenset({0}),
        racks={0: (), 1: ()},
        bag=(),
        scores={0: 0, 1: 0},
        exchange_counts={0: 0, 1: 0},
        consecutive_passes=0,
        last_play=record,
        premoves={},
        turn_number=0 if record is None else record.turn_number + 1,
    )
    return Position(
        board=Board(size=1, bonuses=(None,), tiles=(None,)),
        state=state,
        players=(0, 1),
    )


def make_play(record: PlayRecord) -> JournalEntry:
    return JournalEntry(
        kind=EntryKind.MOVE,
        move=Move(player=record.player, action=LAID),
        actor=record.player,
        reason=None,
        position=make_position(record),
    )


def make_pass(player: int, standing: PlayRecord | None) -> JournalEntry:
    return JournalEntry(
        kind=EntryKind.MOVE,
        move=Move(player=player, action=Pass()),
        actor=player,
        reason=None,
        position=make_position(standing),
    )


def make_exchange(player: int, standing: PlayRecord | None) -> JournalEntry:
    return JournalEntry(
        kind=EntryKind.MOVE,
        move=Move(player=player, action=Exchange(tile_ids=[1])),
        actor=player,
        reason=None,
        position=make_position(standing),
    )


def make_queued(record: PlayRecord, standing: PlayRecord | None) -> JournalEntry:
    return JournalEntry(
        kind=EntryKind.PREMOVE_SET,
        move=Move(player=record.player, action=LAID),
        actor=record.player,
        reason=None,
        position=make_position(standing),
    )


def test_highlights_name_the_best_word_and_the_longest_word() -> None:
    first = make_record(0, (("PODESZWA", 18), ("OS", 4)), 22, 0)
    second = make_record(1, (("DOM", 40),), 40, 1)
    highlights = highlights_of([make_play(first), make_play(second)])
    assert highlights.best_word is not None
    assert highlights.best_word.word == "DOM"
    assert highlights.best_word.points == 40
    assert highlights.best_word.player == 1
    assert highlights.longest_word is not None
    assert highlights.longest_word.word == "PODESZWA"
    assert highlights.longest_word.points == 18
    assert highlights.longest_word.player == 0


def test_the_best_word_is_read_from_the_word_rather_than_the_play() -> None:
    record = make_record(0, (("OS", 4), ("PODESZWA", 18)), 72, 0)
    highlights = highlights_of([make_play(record)])
    assert highlights.best_word is not None
    assert highlights.best_word.word == "PODESZWA"
    assert highlights.best_word.points == 18


def test_the_best_word_ties_to_the_longer() -> None:
    first = make_record(0, (("DOM", 24),), 24, 0)
    second = make_record(1, (("KOTLETY", 24),), 24, 1)
    highlights = highlights_of([make_play(first), make_play(second)])
    assert highlights.best_word is not None
    assert highlights.best_word.word == "KOTLETY"


def test_the_best_word_ties_to_the_earlier_at_equal_length() -> None:
    first = make_record(0, (("DOM", 24),), 24, 0)
    second = make_record(1, (("KOT", 24),), 24, 3)
    highlights = highlights_of([make_play(first), make_play(second)])
    assert highlights.best_word is not None
    assert highlights.best_word.player == 0


def test_longest_word_ties_to_the_higher_scoring() -> None:
    first = make_record(0, (("KOTY", 8),), 8, 0)
    second = make_record(1, (("DOMY", 21),), 21, 1)
    highlights = highlights_of([make_play(first), make_play(second)])
    assert highlights.longest_word is not None
    assert highlights.longest_word.word == "DOMY"


def test_longest_word_ties_to_the_earlier_at_equal_points() -> None:
    first = make_record(0, (("KOTY", 8),), 8, 0)
    second = make_record(1, (("DOMY", 8),), 8, 1)
    highlights = highlights_of([make_play(first), make_play(second)])
    assert highlights.longest_word is not None
    assert highlights.longest_word.word == "KOTY"


def test_one_word_can_be_both_the_best_and_the_longest() -> None:
    first = make_record(0, (("DOM", 12),), 12, 0)
    second = make_record(1, (("KOTLETY", 30),), 80, 1)
    highlights = highlights_of([make_play(first), make_play(second)])
    assert highlights.best_word == highlights.longest_word
    assert highlights.best_word is not None
    assert highlights.best_word.word == "KOTLETY"


def test_a_highlight_names_the_turn_it_was_made_on() -> None:
    first = make_record(0, (("KOTLETY", 30),), 30, 4)
    second = make_record(1, (("DOM", 40),), 40, 7)
    highlights = highlights_of([make_play(first), make_play(second)])
    assert highlights.best_word is not None
    assert highlights.best_word.turn_number == 7
    assert highlights.longest_word is not None
    assert highlights.longest_word.turn_number == 4


def test_a_crossing_word_can_be_the_longest() -> None:
    record = make_record(0, (("OS", 4), ("PODESZWA", 18)), 22, 0)
    highlights = highlights_of([make_play(record)])
    assert highlights.longest_word is not None
    assert highlights.longest_word.word == "PODESZWA"


def test_a_game_without_plays_has_no_highlights() -> None:
    highlights = highlights_of([make_pass(0, None), make_exchange(1, None)])
    assert highlights.best_word is None
    assert highlights.longest_word is None


def test_an_empty_journal_has_no_highlights() -> None:
    highlights = highlights_of([])
    assert highlights.best_word is None
    assert highlights.longest_word is None


def test_passes_and_queued_moves_leave_the_highlights_on_the_plays() -> None:
    played = make_record(0, (("DOM", 12),), 12, 0)
    queued = make_record(1, (("KOTLETY", 90),), 90, 9)
    highlights = highlights_of(
        [
            make_play(played),
            make_pass(1, played),
            make_queued(queued, played),
            make_exchange(0, played),
        ]
    )
    assert highlights.best_word is not None
    assert highlights.best_word.points == 12
    assert highlights.longest_word is not None
    assert highlights.longest_word.word == "DOM"
