from typing import Final, Protocol

from lexica.morph.mapping import build_analysis
from lexica.morph.models import Analysis, MorphSource

Interpretation = tuple[str, str, str, list[str], list[str]]

_IGNORED_PREFIXES: Final[frozenset[str]] = frozenset({"ign", "xx"})


class MorfeuszAnalyzer(Protocol):
    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]: ...

    def generate(self, lemma: str) -> list[Interpretation]: ...

    def dict_id(self) -> str: ...


def analyse_word(analyzer: MorfeuszAnalyzer, word: str) -> tuple[Analysis, ...]:
    analyses: list[Analysis] = []
    for _, _, (surface, lemma, tag, names, qualifiers) in analyzer.analyse(word):
        if tag.split(":", 1)[0] in _IGNORED_PREFIXES:
            continue
        analyses.append(
            build_analysis(
                surface.upper(),
                lemma.upper(),
                tag,
                MorphSource.SGJP,
                tuple(dict.fromkeys((*names, *qualifiers))),
            )
        )
    return tuple(analyses)
