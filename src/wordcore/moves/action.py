from typing import Annotated, Literal

from pydantic import Field

from wordcore.models.base import BaseFrozen


class PlayPlacement(BaseFrozen):
    tile_id: int
    row: int
    column: int


class Play(BaseFrozen):
    kind: Literal["play"] = "play"
    placements: tuple[PlayPlacement, ...]


class Exchange(BaseFrozen):
    kind: Literal["exchange"] = "exchange"
    tile_ids: tuple[int, ...]


class Pass(BaseFrozen):
    kind: Literal["pass"] = "pass"


AnyAction = Annotated[Play | Exchange | Pass, Field(discriminator="kind")]


class Move(BaseFrozen):
    player: int
    action: AnyAction
