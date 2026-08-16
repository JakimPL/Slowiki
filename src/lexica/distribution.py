from collections import Counter
from collections.abc import Iterable


def letter_counts(words: Iterable[str]) -> Counter[str]:
    return Counter(letter for word in words for letter in word.upper())
