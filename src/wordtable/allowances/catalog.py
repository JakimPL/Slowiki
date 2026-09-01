from pydantic import model_validator

from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.base import BaseFrozen
from wordtable.allowances.allowance import Allowance
from wordtable.allowances.name import SettingName


class AllowanceCatalog(BaseFrozen):
    allowances: tuple[Allowance, ...]

    @model_validator(mode="after")
    def _ensure_each_setting_is_allowed_once(self) -> "AllowanceCatalog":
        stated = [allowance.setting for allowance in self.allowances]
        repeated = sorted({setting for setting in stated if stated.count(setting) > 1})
        if repeated:
            raise InvalidConfiguration(f"the allowances state {', '.join(repeated)} more than once")

        return self

    @model_validator(mode="after")
    def _ensure_every_setting_is_allowed(self) -> "AllowanceCatalog":
        unallowed = sorted(set(SettingName) - {allowance.setting for allowance in self.allowances})
        if unallowed:
            raise InvalidConfiguration(f"the allowances leave {', '.join(unallowed)} undescribed")

        return self

    def by_setting(self) -> dict[SettingName, Allowance]:
        return {allowance.setting: allowance for allowance in self.allowances}
