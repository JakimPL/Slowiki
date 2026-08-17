from wordcore.models.base import BaseFrozen
from wordcore.rules.score.word import ScoredWord


class PlayRecord(BaseFrozen):
    player: int
    indices: tuple[int, ...]
    words: tuple[ScoredWord, ...]
    points: int
    bingo: int
    turn_number: int
