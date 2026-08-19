from lexica.lore.analysis_source import AnalysisSource
from lexica.lore.lexeme_id import LexemeId
from wordcore.models.base import BaseFrozen


class VariantRecord(BaseFrozen):
    form: str
    tag: str
    source: AnalysisSource
    in_dictionary: bool


class ClassRecord(BaseFrozen):
    lexeme: LexemeId
    base: str
    variants: tuple[VariantRecord, ...]


class ClassStore(BaseFrozen):
    entries: dict[str, tuple[LexemeId, ...]]
    classes: dict[LexemeId, ClassRecord]
    unknown: tuple[str, ...]
