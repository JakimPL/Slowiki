from typing import Annotated, Final

from pydantic import Field, field_validator, model_validator

from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordcore.models.letters import CanonicalSymbol, TileCount
from wordcore.tiles.blank import BLANK_CATEGORY
from wordtable.names import PresetName
from wordtable.presets.adjustment import LetterAdjustment

MIN_SEATS: Final = 1
MAX_SEATS: Final = 8
MIN_RACK_SIZE: Final = 1
MAX_RACK_SIZE: Final = 15
MAX_BLANKS: Final = 20
MAX_EXCHANGE_LIMIT: Final = 20
MAX_BINGO_BONUS: Final = 200
MAX_PASS_END_ROUNDS: Final = 10
MAX_SCORELESS_END_LIMIT: Final = 50
MIN_PER_TURN_SECONDS: Final = 5
MAX_PER_TURN_SECONDS: Final = 3600
MIN_TOTAL_SECONDS: Final = 30
MAX_TOTAL_SECONDS: Final = 7200
MAX_INCREMENT_SECONDS: Final = 300

SeatCount = Annotated[int, Field(ge=MIN_SEATS, le=MAX_SEATS)]
RackSize = Annotated[int, Field(ge=MIN_RACK_SIZE, le=MAX_RACK_SIZE)]
BlankCount = Annotated[int, Field(ge=0, le=MAX_BLANKS)]
OpeningTiles = Annotated[int, Field(ge=1, le=MAX_RACK_SIZE)]
BingoTiles = Annotated[int, Field(ge=1, le=MAX_RACK_SIZE)]
ExchangeLimit = Annotated[int, Field(ge=0, le=MAX_EXCHANGE_LIMIT)]
BingoBonus = Annotated[int, Field(ge=0, le=MAX_BINGO_BONUS)]
PassEndRounds = Annotated[int, Field(ge=1, le=MAX_PASS_END_ROUNDS)]
ScorelessEndLimit = Annotated[int, Field(ge=1, le=MAX_SCORELESS_END_LIMIT)]
PerTurnSeconds = Annotated[int, Field(ge=MIN_PER_TURN_SECONDS, le=MAX_PER_TURN_SECONDS)]
TotalSeconds = Annotated[int, Field(ge=MIN_TOTAL_SECONDS, le=MAX_TOTAL_SECONDS)]
IncrementSeconds = Annotated[int, Field(ge=0, le=MAX_INCREMENT_SECONDS)]


class RulesConfig(BaseFrozen):
    board: PresetName
    alphabet: PresetName
    distribution: PresetName
    dictionary: DictionaryName
    seats: SeatCount
    rack_size: RackSize | None
    blanks: BlankCount
    validate_on_play: bool
    premoves: bool
    pass_allowed: bool
    exchange_limit: ExchangeLimit | None
    exchange_min_bag: TileCount
    opening_tiles: OpeningTiles
    opening_covers_center: bool
    bingo_bonus: BingoBonus
    bingo_tiles: BingoTiles | None
    going_out_award: bool
    pass_end_rounds: PassEndRounds | None
    scoreless_end_limit: ScorelessEndLimit | None
    per_turn_seconds: PerTurnSeconds | None
    total_seconds: TotalSeconds | None
    increment_seconds: IncrementSeconds
    letters: dict[CanonicalSymbol, LetterAdjustment]

    @field_validator("letters", mode="before")
    @classmethod
    def _ensure_each_symbol_is_adjusted_once(cls, letters: object) -> object:
        if not isinstance(letters, dict):
            return letters

        written = [str(symbol).upper() for symbol in letters]
        repeated = "".join(sorted({symbol for symbol in written if written.count(symbol) > 1}))
        if repeated:
            raise InvalidConfiguration(f"rules adjust {repeated} more than once")

        return letters

    @model_validator(mode="after")
    def _ensure_an_end_limit(self) -> "RulesConfig":
        if self.seats > 1 and self.pass_end_rounds is None and self.scoreless_end_limit is None:
            raise InvalidConfiguration(
                "a table seating several players needs pass_end_rounds or scoreless_end_limit"
            )

        return self

    @model_validator(mode="after")
    def _ensure_one_seat_holds_the_whole_bag(self) -> "RulesConfig":
        if self.rack_size is None and self.seats > 1:
            raise InvalidConfiguration("a table dealing the whole bag seats one player")

        return self

    @model_validator(mode="after")
    def _ensure_a_bingo_fits_the_rack(self) -> "RulesConfig":
        if self.bingo_tiles is None or self.rack_size is None:
            return self

        if self.bingo_tiles > self.rack_size:
            raise InvalidConfiguration(
                f"a bingo of {self.bingo_tiles} tiles overruns a rack of {self.rack_size}"
            )

        return self

    @model_validator(mode="after")
    def _ensure_the_rack_can_open(self) -> "RulesConfig":
        if self.rack_size is not None and self.opening_tiles > self.rack_size:
            raise InvalidConfiguration(
                f"an opening word of {self.opening_tiles} tiles overruns "
                f"a rack of {self.rack_size}"
            )

        return self

    @model_validator(mode="after")
    def _ensure_the_blank_keeps_its_category(self) -> "RulesConfig":
        claimed = sorted(
            symbol
            for symbol, adjustment in self.letters.items()
            if adjustment.category == BLANK_CATEGORY
        )
        if claimed:
            raise InvalidConfiguration(
                f"the category '{BLANK_CATEGORY}' belongs to blank tiles, "
                f"and {''.join(claimed)} claims it"
            )

        return self


def restated(rules: RulesConfig, changes: dict[str, object]) -> RulesConfig:
    return RulesConfig.model_validate({**rules.model_dump(), **changes})
