from collections.abc import Iterable, Mapping

from lexica.lore.analysis import Analysis
from lexica.lore.analysis_source import AnalysisSource
from lexica.lore.lexeme_id import LexemeId
from lexica.sources.sgjp import MorfeuszEngine, generate_paradigm

Paradigms = Mapping[LexemeId, tuple[tuple[str, str], ...]]


def paradigms_of(engine: MorfeuszEngine, analyses: Iterable[Analysis]) -> Paradigms:
    paradigms: dict[LexemeId, tuple[tuple[str, str], ...]] = {}
    for lexeme, source_lemmas in _sgjp_lemmas(analyses).items():
        forms: set[tuple[str, str]] = set()
        for source_lemma in sorted(source_lemmas):
            forms.update(generate_paradigm(engine, source_lemma))
        if forms:
            paradigms[lexeme] = tuple(sorted(forms))
    return paradigms


def _sgjp_lemmas(analyses: Iterable[Analysis]) -> dict[LexemeId, set[str]]:
    source_lemmas: dict[LexemeId, set[str]] = {}
    for analysis in analyses:
        if analysis.source is not AnalysisSource.SGJP:
            continue
        source_lemmas.setdefault(analysis.lexeme, set()).add(analysis.source_lemma)
    return source_lemmas
