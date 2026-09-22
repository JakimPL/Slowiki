from pathlib import Path

from lexica.artifact.formats import ARTIFACT_FORMATS
from lexica.artifact.kind import ArtifactKind
from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.sources.record import read_release_record
from wordtable.sources.releases import POLIMORF_RELEASE

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DICTIONARIES_DIR = PROJECT_ROOT / "dictionaries"
DICTIONARY_SOURCES_DIR = DICTIONARIES_DIR / "sources"
POLIMORF_TABLE = DICTIONARY_SOURCES_DIR / POLIMORF_RELEASE.filename
RUN_CONFIG_FILE = CONFIG_DIR / "config.yaml"
FRONTEND_DIST_DIR = PROJECT_ROOT / "build" / "frontend"
ASSETS_DIR = PROJECT_ROOT / "assets"
ARCHIVE_SUFFIX = ".zip"
SJP_RELEASE_RECORD_NAME = "sjp.release.json"

CONFIGURATION_ALLOWANCES_FILE = Path("allowances.yaml")
CONFIGURATION_SCHEMES_PATH = Path("schemes")
CONFIGURATION_BOARDS_PATH = Path("presets") / "boards"
CONFIGURATION_ALPHABETS_PATH = Path("presets") / "alphabets"
CONFIGURATION_DISTRIBUTIONS_PATH = Path("presets") / "distributions"
CONFIGURATION_STYLES_PATH = Path("styles")


def configuration_file(kind: Path, name: str) -> Path:
    return kind / f"{name}.yaml"


def sjp_release_record() -> Path:
    return DICTIONARIES_DIR / SJP_RELEASE_RECORD_NAME


def dictionary_known(name: DictionaryName) -> bool:
    match name:
        case DictionaryName.SJP:
            return sjp_release_record().is_file()
        case DictionaryName.OSPS | DictionaryName.ENGLISH:
            return True


def archive_path(stem: str) -> Path:
    return DICTIONARIES_DIR / f"{stem}{ARCHIVE_SUFFIX}"


def compiled_name(stem: str, kind: ArtifactKind) -> str:
    return f"{stem}.{kind}.v{ARTIFACT_FORMATS[kind]}.lexicon"


def dictionary_archive(name: DictionaryName) -> Path:
    return archive_path(_dictionary_stem(name))


def dictionary_compiled(name: DictionaryName, kind: ArtifactKind) -> Path:
    return DICTIONARIES_DIR / compiled_name(_dictionary_stem(name), kind)


def dictionary_coverage(name: DictionaryName) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.coverage.json"


def dictionary_unread(name: DictionaryName) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.unread.txt"


def dictionary_overrides(name: DictionaryName) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.morph.yaml"


def dictionary_manifest(name: DictionaryName) -> Path:
    return DICTIONARIES_DIR / f"{_dictionary_stem(name)}.manifest.json"


def _dictionary_stem(name: DictionaryName) -> str:
    match name:
        case DictionaryName.SJP:
            return _recorded_sjp_stem()
        case DictionaryName.OSPS:
            return "osps"
        case DictionaryName.ENGLISH:
            return "english"


def _recorded_sjp_stem() -> str:
    record = read_release_record(sjp_release_record())
    if record is None:
        raise InvalidConfiguration(
            f"no SJP release recorded at {sjp_release_record()}; run 'wordtable fetch'"
        )

    return record.stem
