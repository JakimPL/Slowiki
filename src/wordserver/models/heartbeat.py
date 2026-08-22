from wordcore.models.base import BaseFrozen


class HeartbeatView(BaseFrozen):
    server_time: float
