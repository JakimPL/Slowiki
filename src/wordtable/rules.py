from pydantic import field_validator

from lexica.names import DictionaryName
from wordcore.models.base import BaseFrozen
from wordcore.models.letters import CanonicalSymbol
from wordtable.names import PresetName
from wordtable.presets.adjustment import LetterAdjustment


class RulesConfig(BaseFrozen):
    board: PresetName
    alphabet: PresetName
    distribution: PresetName
    dictionary: DictionaryName
    seats: int
    rack_size: int | None
    blanks: int
    validate_on_play: bool
    premoves: bool
    pass_allowed: bool
    exchange_limit: int | None
    exchange_min_bag: int
    opening_tiles: int
    opening_covers_center: bool
    bingo_bonus: int
    bingo_tiles: int | None
    going_out_award: bool
    pass_end_rounds: int | None
    scoreless_end_limit: int | None
    per_turn_seconds: int | None
    total_seconds: int | None
    increment_seconds: int
    letters: dict[CanonicalSymbol, LetterAdjustment]

    @field_validator("letters", mode="before")
    @classmethod
    def _ensure_each_symbol_is_adjusted_once(cls, letters: object) -> object:
        if not isinstance(letters, dict):
            return letters

        written = [str(symbol).upper() for symbol in letters]
        repeated = "".join(sorted({symbol for symbol in written if written.count(symbol) > 1}))
        if repeated:
            raise ValueError(f"rules adjust {repeated} more than once")

        return letters


def restated(rules: RulesConfig, changes: dict[str, object]) -> RulesConfig:
    return RulesConfig.model_validate({**rules.model_dump(), **changes})
