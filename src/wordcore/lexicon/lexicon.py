from __future__ import annotations

from bisect import bisect_left
from collections.abc import Iterable

from wordcore.lexicon.verdict import WordVerdict
from wordcore.lexicon.wordclass import WordClass
from wordcore.models.base import BaseFrozen


class TextLexicon(BaseFrozen):
    words: tuple[str, ...]

    def judge(self, word: str) -> WordVerdict:
        normalized = word.upper()
        index = bisect_left(self.words, normalized)
        if index < len(self.words) and self.words[index] == normalized:
            return WordVerdict(allowed=True)

        return WordVerdict(allowed=False, reason="absent")

    def has_prefix(self, prefix: str) -> bool:
        normalized = prefix.upper()
        index = bisect_left(self.words, normalized)
        return index < len(self.words) and self.words[index].startswith(normalized)

    def class_infos(self, _word: str) -> tuple[WordClass, ...]:
        return ()

    @classmethod
    def from_words(cls, words: Iterable[str]) -> TextLexicon:
        normalized = sorted({word.upper() for word in words})
        return cls(words=tuple(normalized))
