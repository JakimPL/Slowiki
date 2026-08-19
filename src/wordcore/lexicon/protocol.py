from typing import Protocol

from wordcore.lexicon.verdict import WordVerdict


class Lexicon(Protocol):
    def judge(self, word: str) -> WordVerdict: ...

    def has_prefix(self, prefix: str) -> bool: ...
