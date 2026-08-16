from wordcore.models.base import BaseFrozen


class ScoredWord(BaseFrozen):
    text: str
    points: int
