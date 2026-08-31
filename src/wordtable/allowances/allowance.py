from wordcore.models.base import BaseFrozen
from wordtable.allowances.group import SettingGroup
from wordtable.allowances.kind import SettingKind
from wordtable.allowances.name import SettingName
from wordtable.allowances.tier import SettingTier


class Allowance(BaseFrozen):
    setting: SettingName
    group: SettingGroup
    tier: SettingTier
    kind: SettingKind
    offered: tuple[int, ...] | None = None
