from enum import StrEnum


class Phase(StrEnum):
    TURN = "turn"
    GAME_OVER = "game_over"
    UNRESOLVED = "unresolved"


def finished(phase: Phase) -> bool:
    return phase in (Phase.GAME_OVER, Phase.UNRESOLVED)
