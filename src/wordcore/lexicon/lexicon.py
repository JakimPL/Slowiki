from bisect import bisect_left
from collections.abc import Iterable
from typing import Protocol

from wordcore.models.base import BaseFrozen


class WordVerdict(BaseFrozen):
    allowed: bool
    reason: str | None = None


class Lexicon(Protocol):
    def judge(self, word: str) -> WordVerdict:
        ...

    def has_prefix(self, prefix: str) -> bool:
        ...


class TextLexicon(BaseFrozen):
    words: tuple[str, ...]

    def judge(self, word: str) -> WordVerdict:
        normalized = word.lower()
        index = bisect_left(self.words, normalized)
        if index < len(self.words) and self.words[index] == normalized:
            return WordVerdict(allowed=True)
        return WordVerdict(allowed=False, reason="absent")

    def has_prefix(self, prefix: str) -> bool:
        normalized = prefix.lower()
        index = bisect_left(self.words, normalized)
        return index < len(self.words) and self.words[index].startswith(normalized)

    @classmethod
    def from_words(cls, words: Iterable[str]) -> "TextLexicon":
        normalized = sorted({word.lower() for word in words})
        return cls(words=tuple(normalized))
