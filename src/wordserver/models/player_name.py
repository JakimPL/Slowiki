from typing import Annotated, Final

from pydantic import StringConstraints

MAX_PLAYER_NAME_LENGTH: Final = 32

PlayerName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_PLAYER_NAME_LENGTH),
]
