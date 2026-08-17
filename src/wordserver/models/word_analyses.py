from lexica.morph.models import Analysis
from wordcore.models.base import BaseFrozen


class WordAnalyses(BaseFrozen):
    word: str
    analyses: tuple[Analysis, ...]
