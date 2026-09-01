from typing import Annotated, Final

from pydantic import StringConstraints

MAX_PRESET_NAME_LENGTH: Final = 32

PresetName = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z][a-z0-9-]*$", max_length=MAX_PRESET_NAME_LENGTH),
]
