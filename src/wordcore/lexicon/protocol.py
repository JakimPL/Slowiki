from typing import Protocol

from wordcore.lexicon.verdict import WordVerdict
from wordcore.lexicon.wordclass import WordClass


class Lexicon(Protocol):
    def judge(self, word: str) -> WordVerdict: ...

    def has_prefix(self, prefix: str) -> bool: ...

    def class_infos(self, word: str) -> tuple[WordClass, ...]: ...

    def analysis_rows(self, word: str) -> tuple[tuple[str, str, str], ...]: ...
