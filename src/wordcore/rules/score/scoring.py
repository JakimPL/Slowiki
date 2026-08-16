from wordcore.board.board import Board
from wordcore.board.bonus import Bonus, BonusKind
from wordcore.rules.score.move import MoveScore
from wordcore.rules.score.word import ScoredWord
from wordcore.rules.words.formed import FormedWord
from wordcore.rules.words.placement import Placement
from wordcore.tiles.tile import Tile


def score_move(
    board: Board,
    words: tuple[FormedWord, ...],
    bingo: int,
) -> MoveScore:
    scored = tuple(ScoredWord(text=word.text, points=_score_word(board, word)) for word in words)
    return MoveScore(
        points=sum(word.points for word in scored) + bingo,
        words=scored,
        bingo=bingo,
    )


def _score_word(board: Board, word: FormedWord) -> int:
    letter_sum = sum(_tile_points(board, placement, word) for placement in word.tiles)
    return letter_sum * _word_multiplier(board, word)


def _tile_points(board: Board, placement: Placement, word: FormedWord) -> int:
    value = placement.tile.value
    if _is_new(board, placement, word):
        value *= _letter_bonus(board.bonus_at(placement.row, placement.column), placement.tile)

    return value


def _word_multiplier(board: Board, word: FormedWord) -> int:
    multiplier = 1
    for placement in word.tiles:
        if not _is_new(board, placement, word):
            continue

        bonus = board.bonus_at(placement.row, placement.column)
        if bonus is not None and bonus.kind == BonusKind.WORD_MULTIPLIER:
            multiplier *= bonus.multiplier

    return multiplier


def _is_new(board: Board, placement: Placement, word: FormedWord) -> bool:
    return board.index(placement.row, placement.column) in word.new_indices


def _letter_bonus(bonus: Bonus | None, tile: Tile) -> int:
    if bonus is None:
        return 1

    if bonus.kind == BonusKind.LETTER_MULTIPLIER:
        return bonus.multiplier

    if bonus.kind == BonusKind.CATEGORY_MULTIPLIER and tile.category == bonus.category:
        return bonus.multiplier

    return 1
