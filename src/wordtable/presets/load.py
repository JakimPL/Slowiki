from pathlib import Path

from wordcore.board.preset import BoardPreset
from wordtable.documents import read_named
from wordtable.paths import (
    CONFIGURATION_ALPHABETS_PATH,
    CONFIGURATION_BOARDS_PATH,
    CONFIGURATION_DISTRIBUTIONS_PATH,
)
from wordtable.presets.alphabet import AlphabetPreset
from wordtable.presets.distribution import DistributionPreset


def list_presets(directory: Path, kind: Path) -> tuple[str, ...]:
    return tuple(sorted(path.stem for path in (directory / kind).glob("*.yaml")))


def load_board_preset(directory: Path, name: str) -> BoardPreset:
    return BoardPreset.model_validate(read_named(directory, CONFIGURATION_BOARDS_PATH, name))


def load_alphabet_preset(directory: Path, name: str) -> AlphabetPreset:
    return AlphabetPreset.model_validate(read_named(directory, CONFIGURATION_ALPHABETS_PATH, name))


def load_distribution_preset(directory: Path, name: str) -> DistributionPreset:
    return DistributionPreset.model_validate(
        read_named(directory, CONFIGURATION_DISTRIBUTIONS_PATH, name)
    )
