from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Letter
from wordserver.models.feedback import FeedbackOffered
from wordtable.names import PresetName
from wordtable.rules import RulesConfig
from wordtable.scheme import SpecimenWord


class TableDescription(BaseFrozen):
    code: str | None
    scheme: PresetName
    specimen: SpecimenWord
    rules: RulesConfig
    feedback: FeedbackOffered
    alphabet: tuple[Letter, ...]
    distribution: dict[str, int]
    blanks: int
