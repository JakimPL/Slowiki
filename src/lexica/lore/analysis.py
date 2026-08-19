from collections.abc import Sequence

from lexica.grammar.inflection import Inflection
from lexica.grammar.parse import inflection_of, part_of_speech
from lexica.grammar.qualifier import Qualifier, qualifiers_of
from lexica.lore.analysis_source import AnalysisSource, dialect_of
from lexica.lore.lexeme_id import LexemeId, lexeme_id_from_lemma
from wordcore.models.base import BaseFrozen


class Analysis(BaseFrozen):
    surface: str
    lexeme: LexemeId
    tag: str
    inflection: Inflection
    source: AnalysisSource
    qualifiers: tuple[Qualifier, ...]


def analysis_of(
    surface: str,
    lemma: str,
    tag: str,
    source: AnalysisSource,
    names: Sequence[str],
    labels: Sequence[str],
) -> Analysis:
    dialect = dialect_of(source)
    return Analysis(
        surface=surface,
        lexeme=lexeme_id_from_lemma(part_of_speech(tag, dialect), lemma),
        tag=tag,
        inflection=inflection_of(tag, dialect),
        source=source,
        qualifiers=qualifiers_of(names, labels),
    )
