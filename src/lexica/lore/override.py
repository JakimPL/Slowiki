from collections.abc import Mapping
from typing import NamedTuple

from lexica.lore.analysis import Analysis, analysis_of
from lexica.lore.analysis_source import AnalysisSource


class OverrideRow(NamedTuple):
    lemma: str
    tag: str


OverrideTable = Mapping[str, tuple[OverrideRow, ...]]


def overridden_analyses(surface: str, rows: tuple[OverrideRow, ...]) -> tuple[Analysis, ...]:
    return tuple(
        analysis_of(surface, row.lemma, row.tag, AnalysisSource.OVERRIDE, (), ()) for row in rows
    )
