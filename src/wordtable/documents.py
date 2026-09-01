from pathlib import Path
from typing import Any

import yaml

from wordcore.errors.exceptions import InvalidConfiguration, MissingConfiguration
from wordtable.paths import configuration_file


def read_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise MissingConfiguration(f"missing config file: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise InvalidConfiguration(f"config file must contain a mapping: {path}")

    return data


def read_named(directory: Path, kind: Path, name: str) -> dict[str, Any]:
    return {**read_mapping(directory / configuration_file(kind, name)), "name": name}
