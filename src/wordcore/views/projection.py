from wordcore.board.board import Board
from wordcore.models.base import BaseFrozen
from wordcore.moves.move import Move
from wordcore.positions.position import Position
from wordcore.rules.rack import rack_of
from wordcore.states.phase import Phase
from wordcore.states.record import PlayRecord
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
    scoreless_turns: int
    last_play: PlayRecord | None
    premove: Move | None
    pending_premoves: frozenset[int]
    out_of_tiles: frozenset[int]
    turn_number: int
    players: tuple[int, ...]


def project(position: Position, observer: int | None) -> PositionView:
    state = position.state
    racks = {
        seat: rack if observer is not None and seat == observer else None
        for seat, rack in state.racks.items()
    }
    premove = state.premoves.get(observer) if observer is not None else None
    pending = frozenset(seat for seat, queued in state.premoves.items() if queued is not None)
    return PositionView(
        board=position.board,
        phase=state.phase,
        to_act=state.to_act,
        racks=racks,
        bag_count=len(state.bag),
        scores=state.scores,
        exchange_counts=state.exchange_counts,
        consecutive_passes=state.consecutive_passes,
        scoreless_turns=state.scoreless_turns,
        last_play=state.last_play,
        premove=premove,
        pending_premoves=pending,
        out_of_tiles=_out_of_tiles(position),
        turn_number=state.turn_number,
        players=position.players,
    )


def _out_of_tiles(position: Position) -> frozenset[int]:
    if position.state.bag:
        return frozenset()

    return frozenset(seat for seat in position.players if not rack_of(position, seat))
