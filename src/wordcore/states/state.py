from enum import StrEnum

from wordcore.moves.action import Move
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import Tile


class Phase(StrEnum):
    TURN = "turn"
    GAME_OVER = "game_over"


class WordState(BaseFrozen):
    phase: Phase
    to_act: frozenset[int]
    racks: dict[int, tuple[Tile, ...] | None]
    bag: tuple[Tile, ...]
    scores: dict[int, int]
    exchange_counts: dict[int, int]
    consecutive_passes: int
    premoves: dict[int, Move | None]
    turn_number: int
