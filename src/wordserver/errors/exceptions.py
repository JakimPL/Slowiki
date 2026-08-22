from wordserver.errors.code import ErrorCode


class TableRefused(Exception):
    code: ErrorCode


class SeatTokenMismatch(TableRefused):
    code = ErrorCode.SEAT_TOKEN_MISMATCH


class TableGathering(TableRefused):
    code = ErrorCode.GATHERING


class RackMismatch(TableRefused):
    code = ErrorCode.RACK_MISMATCH


class OutOfTime(TableRefused):
    code = ErrorCode.OUT_OF_TIME
