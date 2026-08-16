from collections.abc import Iterable


def letter_counts(words: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in words:
        for letter in word.lower():
            counts[letter] = counts.get(letter, 0) + 1
    return counts
