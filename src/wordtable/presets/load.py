from pathlib import Path
from typing import Any

from wordcore.board.preset import BoardPreset
from wordtable.documents import read_mapping
from wordtable.paths import (
    CONFIGURATION_ALPHABETS_PATH,
    CONFIGURATION_BOARDS_PATH,
    CONFIGURATION_DISTRIBUTIONS_PATH,
    configuration_file,
)
from wordtable.presets.alphabet import AlphabetPreset
from wordtable.presets.distribution import DistributionPreset


def load_board_preset(directory: Path, name: str) -> BoardPreset:
    return BoardPreset.model_validate(_named(directory, CONFIGURATION_BOARDS_PATH, name))


def load_alphabet_preset(directory: Path, name: str) -> AlphabetPreset:
    return AlphabetPreset.model_validate(_named(directory, CONFIGURATION_ALPHABETS_PATH, name))


def load_distribution_preset(directory: Path, name: str) -> DistributionPreset:
    return DistributionPreset.model_validate(
        _named(directory, CONFIGURATION_DISTRIBUTIONS_PATH, name)
    )


def _named(directory: Path, kind: Path, name: str) -> dict[str, Any]:
    path = directory / configuration_file(kind, name)
    return {**read_mapping(path), "name": name}
