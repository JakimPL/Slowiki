from wordcore.board.board import Board
from wordcore.models.base import BaseFrozen
from wordcore.moves.action import Move
from wordcore.positions.position import Position
from wordcore.states.state import Phase
from wordcore.tiles.tile import Tile


class PositionView(BaseFrozen):
    board: Board
    phase: Phase
    to_act: frozenset[int]
    racks: dict[int, tuple[Tile, ...] | None]
    bag_count: int
    scores: dict[int, int]
    exchange_counts: dict[int, int]
    consecutive_passes: int
    premoves: dict[int, Move | None]
    turn_number: int
    players: tuple[int, ...]


def project(position: Position, observer: int | None) -> PositionView:
    state = position.state
    racks = {
        seat: rack if observer is not None and seat == observer else None
        for seat, rack in state.racks.items()
    }
    premoves = {
        seat: move if observer is not None and seat == observer else None
        for seat, move in state.premoves.items()
    }
    return PositionView(
        board=position.board,
        phase=state.phase,
        to_act=state.to_act,
        racks=racks,
        bag_count=len(state.bag),
        scores=state.scores,
        exchange_counts=state.exchange_counts,
        consecutive_passes=state.consecutive_passes,
        premoves=premoves,
        turn_number=state.turn_number,
        players=position.players,
    )
