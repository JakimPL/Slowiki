from typing import Final, Protocol

from lexica.morph.mapping import build_analysis
from lexica.morph.models import Analysis, MorphSource
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


def analyse_word_entries(
    analyzer: MorfeuszAnalyzer,
    word: str,
) -> tuple[tuple[str, str, str], ...]:
    rows: list[tuple[str, str, str]] = []
    for _, _, (_, lemma, tag, _, _) in analyzer.analyse(word):
        if tag.split(":", 1)[0] in _IGNORED_PREFIXES:
            continue
        rows.append((lemma.upper(), lemma, tag))
    return tuple(rows)


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
