from wordcore.models.base import BaseFrozen
from wordgames.names import GameName


class TableAdmission(BaseFrozen):
    table_id: str
    code: str
    scheme: str
    game: GameName
    max_players: int
    seat: int
    token: str
    name: str | None
