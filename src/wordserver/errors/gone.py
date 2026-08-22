from wordserver.errors.code import ErrorCode
from wordserver.errors.refusal import Refusal
from wordserver.models.game_record import GameRecord


def table_gone(record: GameRecord | None) -> Refusal:
    if record is None:
        return Refusal(404, "unknown table", ErrorCode.UNKNOWN_TABLE)

    return Refusal(410, "the table has closed", ErrorCode.TABLE_CLOSED)
