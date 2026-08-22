from collections.abc import Mapping
from pathlib import Path

from lexica.build.assemble import assemble_classes
from lexica.build.records import ClassStore
from lexica.lore.analysis import Analysis
from lexica.lore.analysis_source import AnalysisSource
from lexica.lore.lexeme_id import LexemeId
from lexica.sources.polimorf import rescue_analyses
from lexica.sources.sgjp import MorfeuszEngine, analyse_word, generate_paradigm
from wordcore.models.base import BaseFrozen


class AnalysisResult(BaseFrozen):
    store: ClassStore
    sgjp_classified: int
    rescued: int
    dict_id: str


def analyse_dictionary(
    words: tuple[str, ...],
    engine: MorfeuszEngine,
    polimorf_path: Path | None,
) -> AnalysisResult:
    analyses_by_form, sgjp_classified = _analyse_sgjp(words, engine)
    rescued_by_form = _rescue_unknown(analyses_by_form, polimorf_path)
    analyses_by_form.update(rescued_by_form)
    generated = _generate_paradigms(engine, analyses_by_form)
    return AnalysisResult(
        store=assemble_classes(analyses_by_form, frozenset(words), generated),
        sgjp_classified=sgjp_classified,
        rescued=len(rescued_by_form),
        dict_id=engine.dict_id(),
    )


def _analyse_sgjp(
    words: tuple[str, ...],
    engine: MorfeuszEngine,
) -> tuple[dict[str, tuple[Analysis, ...]], int]:
    analyses_by_form: dict[str, tuple[Analysis, ...]] = {}
    classified = 0
    for form in words:
        analyses = analyse_word(engine, form.lower())
        analyses_by_form[form] = analyses
        if analyses:
            classified += 1
    return analyses_by_form, classified


def _rescue_unknown(
    analyses_by_form: Mapping[str, tuple[Analysis, ...]],
    polimorf_path: Path | None,
) -> dict[str, tuple[Analysis, ...]]:
    unknown_forms = frozenset(form for form, analyses in analyses_by_form.items() if not analyses)
    if polimorf_path is None or not unknown_forms:
        return {}
    return rescue_analyses(polimorf_path, unknown_forms)


def _generate_paradigms(
    engine: MorfeuszEngine,
    analyses_by_form: Mapping[str, tuple[Analysis, ...]],
) -> dict[LexemeId, tuple[tuple[str, str], ...]]:
    paradigms: dict[LexemeId, tuple[tuple[str, str], ...]] = {}
    for lexeme, source_lemmas in _sgjp_lemmas(analyses_by_form).items():
        forms: set[tuple[str, str]] = set()
        for source_lemma in sorted(source_lemmas):
            forms.update(generate_paradigm(engine, source_lemma))
        if forms:
            paradigms[lexeme] = tuple(sorted(forms))
    return paradigms


def _sgjp_lemmas(
    analyses_by_form: Mapping[str, tuple[Analysis, ...]],
) -> dict[LexemeId, set[str]]:
    source_lemmas: dict[LexemeId, set[str]] = {}
    for analyses in analyses_by_form.values():
        for analysis in analyses:
            if analysis.source is not AnalysisSource.SGJP:
                continue
            source_lemmas.setdefault(analysis.lexeme, set()).add(analysis.source_lemma)
    return source_lemmas
