from typing import Final

from wordcore.models.base import BaseFrozen
from wordcore.models.letters import MAX_TILE_COUNT
from wordtable.allowances.name import SettingName
from wordtable.rules import (
    MAX_BINGO_BONUS,
    MAX_BLANKS,
    MAX_EXCHANGE_LIMIT,
    MAX_INCREMENT_SECONDS,
    MAX_PASS_END_ROUNDS,
    MAX_PER_TURN_SECONDS,
    MAX_RACK_SIZE,
    MAX_SCORELESS_END_LIMIT,
    MAX_SEATS,
    MAX_TOTAL_SECONDS,
    MIN_PER_TURN_SECONDS,
    MIN_RACK_SIZE,
    MIN_SEATS,
    MIN_TOTAL_SECONDS,
)

BINGO_BONUS_STEP: Final = 5
SECONDS_STEP: Final = 5
SINGLE_STEP: Final = 1


class SettingBounds(BaseFrozen):
    minimum: int
    maximum: int
    step: int
    unlimited: bool


SETTING_BOUNDS: Final[dict[SettingName, SettingBounds]] = {
    SettingName.SEATS: SettingBounds(
        minimum=MIN_SEATS,
        maximum=MAX_SEATS,
        step=SINGLE_STEP,
        unlimited=False,
    ),
    SettingName.RACK_SIZE: SettingBounds(
        minimum=MIN_RACK_SIZE,
        maximum=MAX_RACK_SIZE,
        step=SINGLE_STEP,
        unlimited=True,
    ),
    SettingName.BLANKS: SettingBounds(
        minimum=0,
        maximum=MAX_BLANKS,
        step=SINGLE_STEP,
        unlimited=False,
    ),
    SettingName.EXCHANGE_LIMIT: SettingBounds(
        minimum=0,
        maximum=MAX_EXCHANGE_LIMIT,
        step=SINGLE_STEP,
        unlimited=True,
    ),
    SettingName.EXCHANGE_MIN_BAG: SettingBounds(
        minimum=0,
        maximum=MAX_TILE_COUNT,
        step=SINGLE_STEP,
        unlimited=False,
    ),
    SettingName.OPENING_TILES: SettingBounds(
        minimum=1,
        maximum=MAX_RACK_SIZE,
        step=SINGLE_STEP,
        unlimited=False,
    ),
    SettingName.BINGO_BONUS: SettingBounds(
        minimum=0,
        maximum=MAX_BINGO_BONUS,
        step=BINGO_BONUS_STEP,
        unlimited=False,
    ),
    SettingName.BINGO_TILES: SettingBounds(
        minimum=1,
        maximum=MAX_RACK_SIZE,
        step=SINGLE_STEP,
        unlimited=True,
    ),
    SettingName.PASS_END_ROUNDS: SettingBounds(
        minimum=1,
        maximum=MAX_PASS_END_ROUNDS,
        step=SINGLE_STEP,
        unlimited=True,
    ),
    SettingName.SCORELESS_END_LIMIT: SettingBounds(
        minimum=1,
        maximum=MAX_SCORELESS_END_LIMIT,
        step=SINGLE_STEP,
        unlimited=True,
    ),
    SettingName.PER_TURN_SECONDS: SettingBounds(
        minimum=MIN_PER_TURN_SECONDS,
        maximum=MAX_PER_TURN_SECONDS,
        step=SECONDS_STEP,
        unlimited=True,
    ),
    SettingName.TOTAL_SECONDS: SettingBounds(
        minimum=MIN_TOTAL_SECONDS,
        maximum=MAX_TOTAL_SECONDS,
        step=SECONDS_STEP,
        unlimited=True,
    ),
    SettingName.INCREMENT_SECONDS: SettingBounds(
        minimum=0,
        maximum=MAX_INCREMENT_SECONDS,
        step=SECONDS_STEP,
        unlimited=False,
    ),
}
