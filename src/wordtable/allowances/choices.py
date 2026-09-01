from pathlib import Path

from lexica.names import DictionaryName
from wordtable.allowances.name import SettingName
from wordtable.lexicons import dictionary_ready
from wordtable.paths import (
    CONFIGURATION_ALPHABETS_PATH,
    CONFIGURATION_BOARDS_PATH,
    CONFIGURATION_DISTRIBUTIONS_PATH,
)
from wordtable.presets.load import list_presets


def offered_choices(directory: Path) -> dict[SettingName, tuple[str, ...]]:
    return {
        SettingName.BOARD: list_presets(directory, CONFIGURATION_BOARDS_PATH),
        SettingName.ALPHABET: list_presets(directory, CONFIGURATION_ALPHABETS_PATH),
        SettingName.DISTRIBUTION: list_presets(directory, CONFIGURATION_DISTRIBUTIONS_PATH),
        SettingName.DICTIONARY: _ready_dictionaries(),
    }


def _ready_dictionaries() -> tuple[str, ...]:
    return tuple(name.value for name in DictionaryName if dictionary_ready(name))
