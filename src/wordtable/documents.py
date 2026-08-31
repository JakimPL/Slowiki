from pathlib import Path
from typing import Any

import yaml

from wordcore.errors.exceptions import InvalidConfiguration


def read_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise InvalidConfiguration(f"missing config file: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise InvalidConfiguration(f"config file must contain a mapping: {path}")

    return data
