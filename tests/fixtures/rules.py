from typing import Any

from wordtable.paths import CONFIG_DIR
from wordtable.scheme import load_scheme


def stated(changes: dict[str, Any], scheme: str = "literaki") -> dict[str, Any]:
    rules = load_scheme(CONFIG_DIR, scheme).rules.model_dump(mode="json")
    return {**rules, **changes}


def seated(count: int, scheme: str = "literaki") -> dict[str, Any]:
    return stated({"seats": count}, scheme)
