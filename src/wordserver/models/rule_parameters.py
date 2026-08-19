from wordcore.models.base import BaseFrozen
from wordtable.config import TimeConfig


class RuleParameters(BaseFrozen):
    rack_size: int | None
    exchange_limit: int | None
    exchange_min_bag: int
    pass_allowed: bool
    bingo_bonus: int
    validate_on_play: bool
    word_check: bool
    premoves_allowed: bool
    pass_end_limit: int | None
    scoreless_end_limit: int | None
    allowed_pos: tuple[str, ...] | None
    base_form_only: bool
    time: TimeConfig
