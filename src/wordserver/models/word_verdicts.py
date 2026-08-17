from wordcore.lexicon.verdict import WordVerdict
from wordcore.models.base import BaseFrozen


class WordVerdicts(BaseFrozen):
    verdicts: dict[str, WordVerdict]
