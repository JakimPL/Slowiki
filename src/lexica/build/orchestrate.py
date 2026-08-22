import itertools
from collections.abc import Mapping
from pathlib import Path

from lexica.build.assemble import assemble_classes
from lexica.build.records import ClassStore
from lexica.lore.analysis import Analysis
from lexica.sources.paradigms import paradigms_of
from lexica.sources.polimorf import rescue_analyses
from lexica.sources.sgjp import MorfeuszEngine, analyse_word
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
    generated = paradigms_of(engine, itertools.chain.from_iterable(analyses_by_form.values()))
    return AnalysisResult(
        store=assemble_classes(analyses_by_form, frozenset(words).__contains__, generated),
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
        analyses = analyse_word(engine, form)
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
