from bisect import bisect_left

from wordcore.lexicon.verdict import WordVerdict
from wordcore.lexicon.wordclass import WordClass
from wordcore.models.base import BaseFrozen


class MorphClass(BaseFrozen):
    class_id: str
    part: str
    lemma: str
    base: str
    source: str
    variants: tuple[str, ...]


class MorphLexicon(BaseFrozen):
    surfaces: tuple[str, ...]
    entries: tuple[tuple[str, ...], ...]
    classes: dict[str, MorphClass]
    unknown: tuple[str, ...]

    def judge(self, word: str) -> WordVerdict:
        normalized = word.upper()
        index = bisect_left(self.surfaces, normalized)
        if index < len(self.surfaces) and self.surfaces[index] == normalized:
            return WordVerdict(allowed=True)

        return WordVerdict(allowed=False, reason="absent")

    def has_prefix(self, prefix: str) -> bool:
        normalized = prefix.upper()
        index = bisect_left(self.surfaces, normalized)
        return index < len(self.surfaces) and self.surfaces[index].startswith(normalized)

    def class_infos(self, word: str) -> tuple[WordClass, ...]:
        normalized = word.upper()
        index = bisect_left(self.surfaces, normalized)
        if index >= len(self.surfaces) or self.surfaces[index] != normalized:
            return ()

        return tuple(
            WordClass(
                class_id=class_id,
                part=self.classes[class_id].part,
                base=self.classes[class_id].base,
            )
            for class_id in self.entries[index]
        )
