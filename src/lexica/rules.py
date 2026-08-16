import re
from collections.abc import Iterable

from wordcore.models.base import BaseFrozen


class DictionaryRules(BaseFrozen):
    min_length: int = 1
    max_length: int | None = None
    excluded_patterns: tuple[str, ...] = ()


def apply_rules(words: Iterable[str], rules: DictionaryRules) -> tuple[str, ...]:
    patterns = tuple(re.compile(pattern) for pattern in rules.excluded_patterns)
    result: list[str] = []
    for word in words:
        if len(word) < rules.min_length:
            continue
        if rules.max_length is not None and len(word) > rules.max_length:
            continue
        if any(pattern.search(word) for pattern in patterns):
            continue
        result.append(word)
    return tuple(result)
