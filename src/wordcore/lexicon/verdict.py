from wordcore.models.base import BaseFrozen


class WordVerdict(BaseFrozen):
    allowed: bool
    reason: str | None = None
