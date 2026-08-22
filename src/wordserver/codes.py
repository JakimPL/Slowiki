import secrets
from typing import Final

from wordserver.models.join_code import JoinCodeShape

JOIN_ALPHABET: Final = "ABCDEFGHJKLMNPQRSTUVWXYZ"
JOIN_CODE_LENGTH: Final = 6


def new_join_code() -> str:
    return "".join(secrets.choice(JOIN_ALPHABET) for _ in range(JOIN_CODE_LENGTH))


def join_code_shape() -> JoinCodeShape:
    return JoinCodeShape(alphabet=JOIN_ALPHABET, length=JOIN_CODE_LENGTH)
