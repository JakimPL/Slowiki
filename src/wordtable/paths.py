from pathlib import Path

from lexica.names import DictionaryName
from wordcore.exceptions import InvalidConfiguration

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DICTIONARIES_DIR = PROJECT_ROOT / "dictionaries"
RUN_CONFIG_FILE = CONFIG_DIR / "config.yaml"
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"

CONFIGURATION_SCHEMES_PATH = Path("schemes")
CONFIGURATION_BOARDS_PATH = Path("presets") / "boards"
CONFIGURATION_TILES_PATH = Path("presets") / "tiles"
CONFIGURATION_STYLES_PATH = Path("styles")


def configuration_file(kind: Path, name: str) -> Path:
    return kind / f"{name}.yaml"


def dictionary_archive(name: DictionaryName) -> Path:
    match name:
        case DictionaryName.SJP:
            return DICTIONARIES_DIR / "sjp-20260803.zip"
        case _:
            raise InvalidConfiguration(f"unknown dictionary: {name}")


def dictionary_compiled(name: DictionaryName) -> Path:
    match name:
        case DictionaryName.SJP:
            return DICTIONARIES_DIR / "sjp-20260803.lexicon"
        case _:
            raise InvalidConfiguration(f"unknown dictionary: {name}")
