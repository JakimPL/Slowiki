from typing import Final, Protocol

from lexica.lore.analysis import Analysis, analysis_of
from lexica.lore.analysis_source import AnalysisSource
from wordcore.errors.exceptions import InvalidConfiguration

try:
    import morfeusz2  # type: ignore[import-untyped]
except ImportError:
    morfeusz2 = None

Interpretation = tuple[str, str, str, list[str], list[str]]

SGJP_DICTIONARY: Final = "pl.sgjp.sgjp-2026.06.01"

_COMPOSITE_PAST: Final = "composite"
_IGNORED_PREFIXES: Final[frozenset[str]] = frozenset({"ign", "xx"})


class MorfeuszEngine(Protocol):
    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]: ...

    def generate(self, lemma: str) -> list[Interpretation]: ...

    def dict_id(self) -> str: ...


def morphology_available() -> bool:
    return morfeusz2 is not None


def build_morfeusz_engine() -> MorfeuszEngine:
    _ensure_morfeusz_available()
    engine: MorfeuszEngine = morfeusz2.Morfeusz(praet=_COMPOSITE_PAST)
    _ensure_pinned_dictionary(engine.dict_id())
    return engine


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


def analyse_word(engine: MorfeuszEngine, surface: str) -> tuple[Analysis, ...]:
    interpretations = head_interpretations(engine.analyse(surface.lower()))
    analyses: list[Analysis] = []
    for _, _, (_, lemma, tag, names, labels) in interpretations:
        if _is_ignored(tag):
            continue
        analyses.append(analysis_of(surface, lemma, tag, AnalysisSource.SGJP, names, labels))
    return tuple(analyses)


def generate_paradigm(engine: MorfeuszEngine, source_lemma: str) -> tuple[tuple[str, str], ...]:
    return tuple(
        (form.upper(), tag)
        for form, _, tag, _, _ in engine.generate(source_lemma)
        if not _is_ignored(tag)
    )


def _is_ignored(tag: str) -> bool:
    return tag.split(":", 1)[0] in _IGNORED_PREFIXES


def _ensure_morfeusz_available() -> None:
    if not morphology_available():
        raise InvalidConfiguration(
            "morfeusz2 is required for the SJP morphology compile; "
            "install it with: uv sync --extra morphology"
        )


def _ensure_pinned_dictionary(dictionary: str) -> None:
    if dictionary != SGJP_DICTIONARY:
        raise InvalidConfiguration(
            f"the morphology build reads the SGJP dictionary {SGJP_DICTIONARY}; "
            f"morfeusz2 offers {dictionary}"
        )
