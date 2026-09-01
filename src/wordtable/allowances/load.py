from pathlib import Path

from wordtable.allowances.catalog import AllowanceCatalog
from wordtable.documents import read_mapping
from wordtable.paths import CONFIGURATION_ALLOWANCES_FILE


def load_allowances(directory: Path) -> AllowanceCatalog:
    return AllowanceCatalog.model_validate(read_mapping(directory / CONFIGURATION_ALLOWANCES_FILE))
