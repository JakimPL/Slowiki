from wordcore.models.base import BaseFrozen
from wordserver.models.player_name import PlayerName
from wordtable.names import PresetName
from wordtable.rules import RulesConfig


class TableRequest(BaseFrozen):
    scheme: PresetName
    name: PlayerName
    rules: RulesConfig | None = None
