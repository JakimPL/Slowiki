from enum import StrEnum

from lexica.grammar.dialect import TagsetDialect


class AnalysisSource(StrEnum):
    SGJP = "sgjp"
    POLIMORF = "polimorf"
    OVERRIDE = "override"


def dialect_of(source: AnalysisSource) -> TagsetDialect:
    match source:
        case AnalysisSource.SGJP | AnalysisSource.OVERRIDE:
            return TagsetDialect.SGJP
        case AnalysisSource.POLIMORF:
            return TagsetDialect.POLIMORF
