from wordcore.models.base import BaseFrozen
from wordserver.models.player_name import PlayerName


class JoinRequest(BaseFrozen):
    name: PlayerName
