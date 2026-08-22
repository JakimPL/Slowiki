from wordcore.positions.position import Position
from wordcore.states.phase import Phase


def abandoned(position: Position) -> Position:
    state = position.state.model_copy(
        update={
            "phase": Phase.UNRESOLVED,
            "to_act": frozenset(),
            "premoves": {seat: None for seat in position.players},
        }
    )
    return position.model_copy(update={"state": state})
