from pathlib import Path

from lexica.artifact.formats import ARTIFACT_FORMATS
from lexica.artifact.kind import ArtifactKind
from lexica.names import DictionaryName
from wordtable.releases import POLIMORF_RELEASE, SJP_RELEASE

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DICTIONARIES_DIR = PROJECT_ROOT / "dictionaries"
DICTIONARY_SOURCES_DIR = DICTIONARIES_DIR / "sources"
POLIMORF_TABLE = DICTIONARY_SOURCES_DIR / POLIMORF_RELEASE.filename
RUN_CONFIG_FILE = CONFIG_DIR / "config.yaml"
FRONTEND_DIST_DIR = PROJECT_ROOT / "build" / "frontend"
ASSETS_DIR = PROJECT_ROOT / "assets"

CONFIGURATION_SCHEMES_PATH = Path("schemes")
CONFIGURATION_BOARDS_PATH = Path("presets") / "boards"
CONFIGURATION_TILES_PATH = Path("presets") / "tiles"
CONFIGURATION_STYLES_PATH = Path("styles")


def configuration_file(kind: Path, name: str) -> Path:
    return kind / f"{name}.yaml"


def dictionary_archive(name: DictionaryName) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.zip"


def dictionary_compiled(name: DictionaryName, kind: ArtifactKind) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.{kind}.v{ARTIFACT_FORMATS[kind]}.lexicon"


def dictionary_coverage(name: DictionaryName) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.coverage.json"


def dictionary_unread(name: DictionaryName) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.unread.txt"


def _dictionary_stem(name: DictionaryName) -> str:
    match name:
        case DictionaryName.SJP:
            return SJP_RELEASE.stem
        case DictionaryName.OSPS:
            return "osps"
        case DictionaryName.ENGLISH:
            return "english"
