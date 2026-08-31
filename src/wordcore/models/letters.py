from typing import Annotated

from pydantic import BeforeValidator, Field, StringConstraints

CanonicalLetter = Annotated[str, StringConstraints(to_upper=True)]
CanonicalSymbol = Annotated[str, StringConstraints(to_upper=True, min_length=1, max_length=1)]
CategoryName = Annotated[str, StringConstraints(min_length=1)]
LetterValue = Annotated[int, Field(ge=0, le=99)]
TileCount = Annotated[int, Field(ge=0, le=99)]


def spelled_out(written: str | list[str]) -> list[str]:
    if isinstance(written, str):
        return list(written)

    return written


Symbols = Annotated[
    tuple[CanonicalSymbol, ...],
    BeforeValidator(spelled_out),
    Field(min_length=1),
]
