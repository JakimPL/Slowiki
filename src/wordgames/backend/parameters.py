from wordcore.models.base import BaseFrozen
from wordcore.rules.ending import Ending


class GameParameters(BaseFrozen):
    rack_size: int | None
    validate_on_play: bool
    exchange_limit: int | None
    exchange_min_bag: int
    pass_allowed: bool
    opening_tiles: int
    opening_covers_center: bool
    pass_end_rounds: int | None
    scoreless_end_limit: int | None
    bingo_bonus: int
    bingo_tiles: int | None
    ending: Ending
    rack_penalties: bool
    going_out_award: bool
    going_out_bonus: int
