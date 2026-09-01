from typing import Final

from fastapi.exceptions import RequestValidationError

from wordserver.errors.code import ErrorCode
from wordserver.errors.refusal import Refusal

_RULES_FIELD: Final = "rules"
_VALUE_ERROR: Final = "value_error"
# Pydantic prefixes a validator's own sentence when it reports the fault.
_VALUE_ERROR_PREFIX: Final = "Value error, "
_MALFORMED: Final = "the request is malformed"


def malformed_request(error: RequestValidationError) -> Refusal:
    stated = _refused_rules(error)
    if stated is None:
        return Refusal(422, _MALFORMED, ErrorCode.MALFORMED_REQUEST)

    return Refusal(422, stated, ErrorCode.RULES_INCONSISTENT)


def _refused_rules(error: RequestValidationError) -> str | None:
    for fault in error.errors():
        if fault.get("type") == _VALUE_ERROR and _inside_the_rules(fault.get("loc", ())):
            return str(fault.get("msg", _MALFORMED)).removeprefix(_VALUE_ERROR_PREFIX)

    return None


def _inside_the_rules(location: tuple[int | str, ...]) -> bool:
    return len(location) > 1 and location[1] == _RULES_FIELD
