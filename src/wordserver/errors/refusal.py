from fastapi.responses import JSONResponse

from wordserver.errors.body import ErrorBody
from wordserver.errors.code import ErrorCode


class Refusal(Exception):
    def __init__(self, status_code: int, detail: str, code: ErrorCode) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.code = code


def refusal_response(
    status_code: int,
    detail: str,
    code: ErrorCode,
) -> JSONResponse:
    body = ErrorBody(detail=detail, code=code)
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json"),
    )
