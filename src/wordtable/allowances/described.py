from pathlib import Path

from wordcore.models.base import BaseFrozen
from wordtable.allowances.allowance import Allowance
from wordtable.allowances.choices import offered_choices
from wordtable.allowances.group import SettingGroup
from wordtable.allowances.kind import SettingKind
from wordtable.allowances.load import load_allowances
from wordtable.allowances.name import SettingName
from wordtable.allowances.tier import SettingTier


class SettingAllowance(BaseFrozen):
    setting: SettingName
    group: SettingGroup
    tier: SettingTier
    kind: SettingKind
    minimum: int | None
    maximum: int | None
    step: int | None
    unlimited: bool
    offered: tuple[int, ...] | None
    choices: tuple[str, ...] | None


def setting_allowances(directory: Path) -> tuple[SettingAllowance, ...]:
    choices = offered_choices(directory)
    return tuple(
        _described(allowance, choices.get(allowance.setting))
        for allowance in load_allowances(directory).allowances
    )


def _described(allowance: Allowance, choices: tuple[str, ...] | None) -> SettingAllowance:
    return SettingAllowance(
        setting=allowance.setting,
        group=allowance.group,
        tier=allowance.tier,
        kind=allowance.kind,
        minimum=allowance.minimum,
        maximum=allowance.maximum,
        step=allowance.step,
        unlimited=allowance.unlimited,
        offered=allowance.offered,
        choices=choices,
    )
