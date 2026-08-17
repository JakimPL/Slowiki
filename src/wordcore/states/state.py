from enum import StrEnum

from wordcore.models.base import BaseFrozen
from wordcore.moves.move import Move
from wordcore.states.record import PlayRecord
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
    scoreless_turns: int = 0
    last_play: PlayRecord | None = None
    premoves: dict[int, Move | None]
    turn_number: int

    def with_premove(self, seat: int, move: Move | None) -> "WordState":
        return self.model_copy(update={"premoves": {**self.premoves, seat: move}})

    def without_premove(self, seat: int) -> "WordState":
        return self.with_premove(seat, None)
