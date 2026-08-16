from wordcore.models.base import BaseFrozen


class GameParameters(BaseFrozen):
    validate_on_play: bool
    exchange_limit: int | None
    pass_allowed: bool
    pass_end_limit: int | None
    scoreless_end_limit: int | None
    bingo_bonus: int
