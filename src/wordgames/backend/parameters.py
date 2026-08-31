from wordcore.models.base import BaseFrozen


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
    rack_penalties: bool
    going_out_award: bool
    going_out_bonus: int
