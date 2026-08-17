from wordcore.models.base import BaseFrozen
from wordtable.catalogue import Offering


class OfferingsResponse(BaseFrozen):
    offerings: tuple[Offering, ...]
