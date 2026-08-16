from pydantic import BaseModel, ConfigDict


class BaseFrozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
