from wordcore.board.board import Board, Bonus, BonusKind
from wordcore.models.base import BaseFrozen
from wordcore.rules.words import FormedWord
from wordcore.tiles.tile import Tile


class ScoredWord(BaseFrozen):
    text: str
    points: int


class MoveScore(BaseFrozen):
    points: int
    words: tuple[ScoredWord, ...]
    bingo: int


def score_move(board: Board, words: tuple[FormedWord, ...], bingo: int) -> MoveScore:
    scored = tuple(ScoredWord(text=word.text, points=_score_word(board, word)) for word in words)
    return MoveScore(
        points=sum(word.points for word in scored) + bingo,
        words=scored,
        bingo=bingo,
    )


def _score_word(board: Board, word: FormedWord) -> int:
    letter_sum = 0
    for word_tile in word.tiles:
        value = word_tile.tile.value
        if board.index(word_tile.row, word_tile.column) in word.new_indices:
            value *= _letter_bonus(board.bonus_at(word_tile.row, word_tile.column), word_tile.tile)
        letter_sum += value
    multiplier = 1
    for word_tile in word.tiles:
        if board.index(word_tile.row, word_tile.column) not in word.new_indices:
            continue
        bonus = board.bonus_at(word_tile.row, word_tile.column)
        if bonus is not None and bonus.kind == BonusKind.WORD_MULTIPLIER:
            multiplier *= bonus.multiplier
    return letter_sum * multiplier


def _letter_bonus(bonus: Bonus | None, tile: Tile) -> int:
    if bonus is None:
        return 1
    if bonus.kind == BonusKind.LETTER_MULTIPLIER:
        return bonus.multiplier
    if bonus.kind == BonusKind.CATEGORY_MULTIPLIER and tile.category == bonus.category:
        return bonus.multiplier
    return 1
