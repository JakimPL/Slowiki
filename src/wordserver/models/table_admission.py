from wordcore.models.base import BaseFrozen
from wordtable.names import PresetName


class TableAdmission(BaseFrozen):
    table_id: str
    code: str
    scheme: PresetName
    seats: int
    seat: int
    token: str
    name: str | None
