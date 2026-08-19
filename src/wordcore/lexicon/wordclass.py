from wordcore.models.base import BaseFrozen


class WordClass(BaseFrozen):
    class_id: str
    part: str
    base: str
