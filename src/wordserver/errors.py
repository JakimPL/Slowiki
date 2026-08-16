from enum import StrEnum

from fastapi.responses import JSONResponse

from wordcore.exceptions import WordcoreError, rejection_code
from wordcore.models.base import BaseFrozen


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


class ErrorBody(BaseFrozen):
    detail: str
    code: ErrorCode


class Refusal(Exception):
    def __init__(self, status_code: int, detail: str, code: ErrorCode) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.code = code


class SeatTokenMismatch(Exception):
    pass


class TableGathering(Exception):
    pass


def code_for(error: WordcoreError) -> ErrorCode:
    return ErrorCode(rejection_code(error).value)


def refusal_response(status_code: int, detail: str, code: ErrorCode) -> JSONResponse:
    body = ErrorBody(detail=detail, code=code)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))
