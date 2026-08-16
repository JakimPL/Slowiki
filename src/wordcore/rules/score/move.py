from wordcore.models.base import BaseFrozen
from wordcore.rules.score.word import ScoredWord


class MoveScore(BaseFrozen):
    points: int
    words: tuple[ScoredWord, ...]
    bingo: int
