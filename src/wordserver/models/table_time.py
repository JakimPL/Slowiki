from typing import Final

from pydantic import Field

from wordcore.models.base import BaseFrozen

MIN_TOTAL_SECONDS: Final = 30
MAX_TOTAL_SECONDS: Final = 7200
MAX_INCREMENT_SECONDS: Final = 300


class TableTimeRequest(BaseFrozen):
    total_seconds: int | None = Field(default=None, ge=MIN_TOTAL_SECONDS, le=MAX_TOTAL_SECONDS)
    increment_seconds: int = Field(default=0, ge=0, le=MAX_INCREMENT_SECONDS)
