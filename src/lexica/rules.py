import re
from collections.abc import Iterable

from wordcore.models.base import BaseFrozen


class DictionaryRules(BaseFrozen):
    min_length: int = 1
    max_length: int | None = None
    excluded_patterns: tuple[str, ...] = ()


def is_word_too_short(word: str, rules: DictionaryRules) -> bool:
    return len(word) < rules.min_length


def is_word_too_large(word: str, rules: DictionaryRules) -> bool:
    return rules.max_length is not None and len(word) > rules.max_length


def does_word_contain_excluded_pattern(
    word: str,
    rules: DictionaryRules,
) -> bool:
    patterns = tuple(re.compile(pattern) for pattern in rules.excluded_patterns)
    return any(pattern.search(word) for pattern in patterns)


def apply_rules(
    words: Iterable[str],
    rules: DictionaryRules,
) -> tuple[str, ...]:
    result: list[str] = []
    for word in words:
        if is_word_too_short(word, rules):
            continue

        if is_word_too_large(word, rules):
            continue

        if does_word_contain_excluded_pattern(word, rules):
            continue

        result.append(word)

    return tuple(result)
