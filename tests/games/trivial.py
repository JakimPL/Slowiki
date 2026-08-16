import random

from wordcore.board.board import Board
from wordcore.exceptions import IllegalMove
from wordcore.moves.action import Move, Pass
from wordcore.positions.position import Position
from wordcore.states.state import Phase, WordState


class TrivialRules:
    def __init__(self) -> None:
        self.reject_seat: int | None = None

    def initial_position(self, rng: random.Random) -> Position:
        return Position(
            board=Board(size=1, bonuses=(None,), tiles=(None,)),
            state=WordState(
                phase=Phase.TURN,
                to_act=frozenset({0}),
                racks={0: (), 1: ()},
                bag=(),
                scores={0: 0, 1: 0},
                exchange_counts={0: 0, 1: 0},
                consecutive_passes=0,
                premoves={},
                turn_number=0,
            ),
            players=(0, 1),
        )

    def validate(self, position: Position, move: Move) -> None:
        if not isinstance(move.action, Pass):
            raise IllegalMove("only pass is allowed")
        if move.player == self.reject_seat:
            raise IllegalMove("pass is disallowed for this seat")

    def apply(self, position: Position, move: Move, rng: random.Random) -> Position:
        state = position.state
        next_seat = 1 - move.player
        new_state = state.model_copy(
            update={
                "to_act": frozenset({next_seat}),
                "turn_number": state.turn_number + 1,
            }
        )
        return position.model_copy(update={"state": new_state})
