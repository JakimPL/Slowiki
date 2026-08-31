from wordcore.models.base import BaseFrozen


class RackRequest(BaseFrozen):
    tile_ids: tuple[int, ...]
