from wordcore.models.base import BaseFrozen
from wordserver.models.join_code import JoinCodeShape
from wordtable.allowances.described import SettingAllowance
from wordtable.catalog import Offering


class OfferingsResponse(BaseFrozen):
    offerings: tuple[Offering, ...]
    code: JoinCodeShape
    allowances: tuple[SettingAllowance, ...]
