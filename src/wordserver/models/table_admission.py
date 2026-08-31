from wordcore.models.base import BaseFrozen


class TableAdmission(BaseFrozen):
    table_id: str
    code: str
    scheme: str
    max_players: int
    seat: int
    token: str
    name: str | None
