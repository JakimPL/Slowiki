from collections.abc import Mapping
from typing import NamedTuple

from lexica.lore.analysis import Analysis, analysis_of
from lexica.lore.analysis_source import AnalysisSource


class RescueRow(NamedTuple):
    lemma: str
    tag: str
    name: str
    label: str


RescueTable = Mapping[str, tuple[RescueRow, ...]]


def rescued_analyses(surface: str, rows: tuple[RescueRow, ...]) -> tuple[Analysis, ...]:
    return tuple(
        analysis_of(surface, row.lemma, row.tag, AnalysisSource.POLIMORF, (row.name,), (row.label,))
        for row in rows
    )
