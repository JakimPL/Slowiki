from wordcore.models.base import BaseFrozen


class SettingBounds(BaseFrozen):
    minimum: int
    maximum: int
    step: int
    unlimited: bool
