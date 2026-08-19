from wordcore.models.base import BaseFrozen
from wordtable.catalog import Offering


class OfferingsResponse(BaseFrozen):
    offerings: tuple[Offering, ...]
