from wordcore.board.board import Board
from wordcore.models.base import BaseFrozen
from wordcore.states.state import WordState


class Position(BaseFrozen):
    board: Board
    state: WordState
    players: tuple[int, ...]
