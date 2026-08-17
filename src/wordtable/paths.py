from pathlib import Path
from typing import Final

from lexica.names import DictionaryName

LEXICON_FORMAT: Final = 2

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DICTIONARIES_DIR = PROJECT_ROOT / "dictionaries"
RUN_CONFIG_FILE = CONFIG_DIR / "config.yaml"
FRONTEND_DIST_DIR = PROJECT_ROOT / "build" / "frontend"

CONFIGURATION_SCHEMES_PATH = Path("schemes")
CONFIGURATION_BOARDS_PATH = Path("presets") / "boards"
CONFIGURATION_TILES_PATH = Path("presets") / "tiles"
CONFIGURATION_STYLES_PATH = Path("styles")


def configuration_file(kind: Path, name: str) -> Path:
    return kind / f"{name}.yaml"


def dictionary_archive(name: DictionaryName) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.zip"


def dictionary_compiled(name: DictionaryName) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.v{LEXICON_FORMAT}.lexicon"


def _dictionary_stem(name: DictionaryName) -> str:
    match name:
        case DictionaryName.SJP:
            return "sjp-20260803"
        case DictionaryName.OSPS:
            return "osps"
        case DictionaryName.ENGLISH:
            return "english"
