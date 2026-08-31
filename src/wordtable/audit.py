from collections.abc import Callable
from pathlib import Path

from wordcore.models.base import BaseFrozen
from wordtable.catalog import list_schemes
from wordtable.paths import (
    CONFIGURATION_ALPHABETS_PATH,
    CONFIGURATION_BOARDS_PATH,
    CONFIGURATION_DISTRIBUTIONS_PATH,
    CONFIGURATION_STYLES_PATH,
)
from wordtable.presets.load import (
    list_presets,
    load_alphabet_preset,
    load_board_preset,
    load_distribution_preset,
)
from wordtable.settling import resolve_table
from wordtable.style import load_style_tokens


def audit_configuration(directory: Path) -> None:
    _audit_presets(directory)
    _audit_schemes(directory)


def _audit_presets(directory: Path) -> None:
    loaders: dict[Path, Callable[[Path, str], BaseFrozen]] = {
        CONFIGURATION_BOARDS_PATH: load_board_preset,
        CONFIGURATION_ALPHABETS_PATH: load_alphabet_preset,
        CONFIGURATION_DISTRIBUTIONS_PATH: load_distribution_preset,
        CONFIGURATION_STYLES_PATH: load_style_tokens,
    }
    for kind, load in loaders.items():
        for name in list_presets(directory, kind):
            load(directory, name)


def _audit_schemes(directory: Path) -> None:
    for scheme in list_schemes(directory).values():
        resolve_table(directory, scheme, None)
