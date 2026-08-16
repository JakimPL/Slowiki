from wordcore.models.base import BaseFrozen
from wordcore.moves.action import AnyAction


class Move(BaseFrozen):
    player: int
    action: AnyAction
