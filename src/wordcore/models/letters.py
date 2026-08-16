from typing import Annotated

from pydantic import StringConstraints

CanonicalLetter = Annotated[str, StringConstraints(to_upper=True)]
