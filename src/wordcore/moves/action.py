from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field

from wordcore.models.base import BaseFrozen


class ActionKind(StrEnum):
    PLAY = "play"
    EXCHANGE = "exchange"
    PASS = "pass"
    REORDER = "reorder"


class PlayPlacement(BaseFrozen):
    tile_id: int
    row: int
    column: int
    letter: str | None = None


class Play(BaseFrozen):
    kind: Literal[ActionKind.PLAY] = ActionKind.PLAY
    placements: tuple[PlayPlacement, ...]


class Exchange(BaseFrozen):
    kind: Literal[ActionKind.EXCHANGE] = ActionKind.EXCHANGE
    tile_ids: tuple[int, ...]


class Pass(BaseFrozen):
    kind: Literal[ActionKind.PASS] = ActionKind.PASS


class Reorder(BaseFrozen):
    kind: Literal[ActionKind.REORDER] = ActionKind.REORDER
    tile_ids: tuple[int, ...]


AnyAction = Annotated[Play | Exchange | Pass | Reorder, Field(discriminator="kind")]


class Move(BaseFrozen):
    player: int
    action: AnyAction
