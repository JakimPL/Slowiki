from lexica.names import DictionaryName
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Letter
from wordserver.models.rule_parameters import RuleParameters


class TableDescription(BaseFrozen):
    code: str | None
    scheme: str
    seats: int
    dictionary: DictionaryName
    parameters: RuleParameters
    alphabet: tuple[Letter, ...]
    distribution: dict[str, int]
    blanks: int
