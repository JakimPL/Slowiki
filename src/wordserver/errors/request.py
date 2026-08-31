from fastapi.exceptions import RequestValidationError

from wordserver.errors.code import ErrorCode
from wordserver.errors.refusal import Refusal
from wordtable.allowances.name import SettingName

_RULES_FIELD = "rules"


def malformed_request(error: RequestValidationError) -> Refusal:
    setting = _setting_at_fault(error)
    if setting is None:
        return Refusal(422, "the request is malformed", ErrorCode.MALFORMED_REQUEST)

    return Refusal(
        422,
        f"the setting '{setting}' is outside what a table may ask for",
        ErrorCode.SETTING_OUT_OF_RANGE,
    )


def _setting_at_fault(error: RequestValidationError) -> SettingName | None:
    for fault in error.errors():
        named = _named_setting(fault.get("loc", ()))
        if named is not None:
            return named

    return None


def _named_setting(location: tuple[int | str, ...]) -> SettingName | None:
    if len(location) < 3 or location[1] != _RULES_FIELD:
        return None

    stated = str(location[2])
    if stated in set(SettingName):
        return SettingName(stated)

    return None
