from wordcore.models.base import BaseFrozen


class FeedbackOffered(BaseFrozen):
    word_check: bool
    lore: bool
