from enum import StrEnum

from wordcore.errors.exceptions import WordcoreError
from wordcore.errors.rejections import rejection_code


class ErrorCode(StrEnum):
    ILLEGAL_MOVE = "illegal_move"
    NOT_YOUR_TURN = "not_your_turn"
    STALE_POSITION = "stale_position"
    INVALID_WORD = "invalid_word"
    GAME_OVER = "game_over"
    NO_PREMOVE = "no_premove"
    INVALID_CONFIGURATION = "invalid_configuration"
    REJECTED = "rejected"
    UNKNOWN_TABLE = "unknown_table"
    UNKNOWN_CODE = "unknown_code"
    UNKNOWN_SCHEME = "unknown_scheme"
    TABLE_FULL = "table_full"
    SEATS_OUT_OF_RANGE = "seats_out_of_range"
    SEAT_TOKEN_MISMATCH = "seat_token_mismatch"
    GATHERING = "gathering"
    DICTIONARY_UNAVAILABLE = "dictionary_unavailable"


def code_for(error: WordcoreError) -> ErrorCode:
    return ErrorCode(rejection_code(error).value)
