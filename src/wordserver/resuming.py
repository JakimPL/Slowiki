from typing import Final

JOURNAL_START: Final = 0
ID_SEPARATOR: Final = ","


def resume_point(last_event_id: str | None) -> int:
    if last_event_id is None:
        return JOURNAL_START

    seen = _seen_ids(last_event_id)
    if not seen:
        return JOURNAL_START

    return min(seen) + 1


def _seen_ids(last_event_id: str) -> tuple[int, ...]:
    tokens = (token.strip() for token in last_event_id.split(ID_SEPARATOR))
    return tuple(int(token) for token in tokens if token.isascii() and token.isdigit())
