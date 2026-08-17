from wordcore.models.base import BaseFrozen
from wordserver.errors.code import ErrorCode


class ErrorBody(BaseFrozen):
    detail: str
    code: ErrorCode
