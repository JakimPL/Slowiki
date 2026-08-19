from typing import Final, Protocol

from lexica.lore.analysis import Analysis, analysis_of
from lexica.lore.analysis_source import AnalysisSource
from wordcore.errors.exceptions import InvalidConfiguration

try:
    import morfeusz2  # type: ignore[import-untyped]
except ImportError:
    morfeusz2 = None

Interpretation = tuple[str, str, str, list[str], list[str]]

_IGNORED_PREFIXES: Final[frozenset[str]] = frozenset({"ign", "xx"})


class MorfeuszAnalyzer(Protocol):
    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]: ...

    def generate(self, lemma: str) -> list[Interpretation]: ...

    def dict_id(self) -> str: ...


def build_morfeusz_analyzer() -> MorfeuszAnalyzer:
    if morfeusz2 is None:
        raise InvalidConfiguration(
            "morfeusz2 is required for the SJP morphology compile; "
            "install it with: uv sync --extra morphology"
        )
    analyzer: MorfeuszAnalyzer = morfeusz2.Morfeusz()
    return analyzer


def head_interpretations(
    analyses: list[tuple[int, int, Interpretation]],
) -> list[tuple[int, int, Interpretation]]:
    max_end = max((end for _, end, _ in analyses), default=0)
    full = [
        (start, end, analysis) for start, end, analysis in analyses if start == 0 and end == max_end
    ]
    if full:
        return full
    return [(start, end, analysis) for start, end, analysis in analyses if start == 0]


def analyse_word(analyzer: MorfeuszAnalyzer, word: str) -> tuple[Analysis, ...]:
    analyses: list[Analysis] = []
    for _, _, (_, lemma, tag, names, labels) in head_interpretations(analyzer.analyse(word)):
        if tag.split(":", 1)[0] in _IGNORED_PREFIXES:
            continue
        analyses.append(analysis_of(word.upper(), lemma, tag, AnalysisSource.SGJP, names, labels))
    return tuple(analyses)
