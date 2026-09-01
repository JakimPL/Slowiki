from typing import Final

from pydantic import model_validator

from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordtable.allowances.bounds import SettingBounds
from wordtable.allowances.group import SettingGroup
from wordtable.allowances.kind import BOUNDED_KINDS, OPTIONAL_KINDS, SettingKind
from wordtable.allowances.name import SettingName
from wordtable.allowances.tier import SettingTier

UNLIMITED_DEFAULT: Final = False
SMALLEST_STEP: Final = 1


class Allowance(BaseFrozen):
    setting: SettingName
    group: SettingGroup
    tier: SettingTier
    kind: SettingKind
    minimum: int | None = None
    maximum: int | None = None
    step: int | None = None
    unlimited: bool = UNLIMITED_DEFAULT
    offered: tuple[int, ...] | None = None
    choices: tuple[str, ...] | None = None

    def bounds(self) -> SettingBounds | None:
        if self.minimum is None or self.maximum is None or self.step is None:
            return None

        return SettingBounds(
            minimum=self.minimum,
            maximum=self.maximum,
            step=self.step,
            unlimited=self.unlimited,
        )

    @model_validator(mode="after")
    def _ensure_a_bounded_kind_states_a_range(self) -> "Allowance":
        if self.kind in BOUNDED_KINDS and self.bounds() is None:
            raise InvalidConfiguration(
                f"the allowance for {self.setting} takes a minimum, a maximum and a step"
            )

        return self

    @model_validator(mode="after")
    def _ensure_every_other_kind_states_no_range(self) -> "Allowance":
        stated = self.minimum is not None or self.maximum is not None or self.step is not None
        if self.kind not in BOUNDED_KINDS and stated:
            raise InvalidConfiguration(
                f"a {self.kind} allowance holds no range, and {self.setting} states one"
            )

        return self

    @model_validator(mode="after")
    def _ensure_the_range_reads_upward(self) -> "Allowance":
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise InvalidConfiguration(
                f"the allowance for {self.setting} runs from {self.minimum} down to {self.maximum}"
            )

        return self

    @model_validator(mode="after")
    def _ensure_the_step_moves(self) -> "Allowance":
        if self.step is not None and self.step < SMALLEST_STEP:
            raise InvalidConfiguration(f"the allowance for {self.setting} steps by {self.step}")

        return self

    @model_validator(mode="after")
    def _ensure_only_a_choice_names_its_values(self) -> "Allowance":
        if self.choices is not None and self.kind is not SettingKind.CHOICE:
            raise InvalidConfiguration(
                f"a {self.kind} allowance holds no values, and {self.setting} names some"
            )

        return self

    @model_validator(mode="after")
    def _ensure_only_an_optional_setting_lifts_its_limit(self) -> "Allowance":
        if self.unlimited and self.kind not in OPTIONAL_KINDS:
            raise InvalidConfiguration(
                f"a {self.kind} allowance holds a value, and {self.setting} lifts its limit"
            )

        return self
