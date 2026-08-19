from collections.abc import Mapping
from pathlib import Path

from lexica.build.assemble import assemble_classes
from lexica.build.records import ClassStore
from lexica.lore.analysis import Analysis
from lexica.lore.lexeme_id import LexemeId
from lexica.sources.polimorf import rescue_analyses
from lexica.sources.sgjp import MorfeuszAnalyzer, analyse_word
from wordcore.models.base import BaseFrozen


class AnalysisResult(BaseFrozen):
    store: ClassStore
    sgjp_classified: int
    rescued: int
    dict_id: str


def analyse_dictionary(
    words: tuple[str, ...],
    analyzer: MorfeuszAnalyzer,
    polimorf_path: Path | None,
) -> AnalysisResult:
    analyses_by_form, sgjp_classified = _analyse_sgjp(words, analyzer)
    unknown_forms = [form for (form, analyses) in analyses_by_form.items() if not analyses]
    rescued = 0
    if polimorf_path is not None and unknown_forms:
        rescued_by_form = rescue_analyses(
            polimorf_path,
            frozenset(form.lower() for form in unknown_forms),
        )
        for form in unknown_forms:
            analyses = rescued_by_form.get(form.lower())
            if analyses is None:
                continue
            analyses_by_form[form] = analyses
            rescued += 1

    generated = _generate_paradigms(analyzer, analyses_by_form)
    store = assemble_classes(analyses_by_form, frozenset(words), generated)
    return AnalysisResult(
        store=store,
        sgjp_classified=sgjp_classified,
        rescued=rescued,
        dict_id=analyzer.dict_id(),
    )


def _analyse_sgjp(
    words: tuple[str, ...],
    analyzer: MorfeuszAnalyzer,
) -> tuple[dict[str, tuple[Analysis, ...]], int]:
    analyses_by_form: dict[str, tuple[Analysis, ...]] = {}
    classified = 0
    for form in words:
        analyses = analyse_word(analyzer, form.lower())
        analyses_by_form[form] = analyses
        if analyses:
            classified += 1
    return analyses_by_form, classified


def _generate_paradigms(
    _analyzer: MorfeuszAnalyzer,
    _analyses_by_form: Mapping[str, tuple[Analysis, ...]],
) -> dict[LexemeId, tuple[tuple[str, str], ...]]:
    return {}
