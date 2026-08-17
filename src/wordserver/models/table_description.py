from lexica.names import DictionaryName
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Letter
from wordgames.names import GameName
from wordserver.models.rule_parameters import RuleParameters


class TableDescription(BaseFrozen):
    code: str | None
    scheme: str
    game: GameName
    seats: int
    dictionary: DictionaryName
    parameters: RuleParameters
    alphabet: tuple[Letter, ...]
    distribution: dict[str, int]
    blanks: int
