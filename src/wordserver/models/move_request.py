from wordcore.models.base import BaseFrozen
from wordcore.moves.move import Move


class MoveRequest(BaseFrozen):
    move: Move
    base_seq: int
    premove: bool = False
