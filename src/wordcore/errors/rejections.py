from enum import StrEnum

from wordcore.errors.exceptions import (
    GameOver,
    IllegalMove,
    InvalidConfiguration,
    InvalidWord,
    NoPremove,
    NotYourTurn,
    StalePosition,
    WordcoreError,
)


class RejectionCode(StrEnum):
    ILLEGAL_MOVE = "illegal_move"
    NOT_YOUR_TURN = "not_your_turn"
    STALE_POSITION = "stale_position"
    INVALID_WORD = "invalid_word"
    GAME_OVER = "game_over"
    NO_PREMOVE = "no_premove"
    OUT_OF_TIME = "out_of_time"
    INVALID_CONFIGURATION = "invalid_configuration"
    REJECTED = "rejected"


def rejection_code(error: WordcoreError) -> RejectionCode:
    match error:
        case InvalidWord():
            return RejectionCode.INVALID_WORD
        case NotYourTurn():
            return RejectionCode.NOT_YOUR_TURN
        case StalePosition():
            return RejectionCode.STALE_POSITION
        case GameOver():
            return RejectionCode.GAME_OVER
        case NoPremove():
            return RejectionCode.NO_PREMOVE
        case IllegalMove():
            return RejectionCode.ILLEGAL_MOVE
        case InvalidConfiguration():
            return RejectionCode.INVALID_CONFIGURATION
        case _:
            return RejectionCode.REJECTED
