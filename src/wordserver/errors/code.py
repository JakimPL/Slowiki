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
    OUT_OF_TIME = "out_of_time"
    INVALID_CONFIGURATION = "invalid_configuration"
    REJECTED = "rejected"
    UNKNOWN_TABLE = "unknown_table"
    TABLE_CLOSED = "table_closed"
    UNKNOWN_CODE = "unknown_code"
    UNKNOWN_SCHEME = "unknown_scheme"
    UNKNOWN_PRESET = "unknown_preset"
    TABLE_FULL = "table_full"
    SETTING_OUT_OF_RANGE = "setting_out_of_range"
    RULES_INCONSISTENT = "rules_inconsistent"
    MALFORMED_REQUEST = "malformed_request"
    SEAT_TOKEN_MISMATCH = "seat_token_mismatch"
    RACK_MISMATCH = "rack_mismatch"
    GATHERING = "gathering"
    DICTIONARY_UNAVAILABLE = "dictionary_unavailable"
    WORD_CHECK_UNAVAILABLE = "word_check_unavailable"
    LORE_UNAVAILABLE = "lore_unavailable"
    TOO_MANY_WORDS = "too_many_words"


def code_for(error: WordcoreError) -> ErrorCode:
    return ErrorCode(rejection_code(error).value)
