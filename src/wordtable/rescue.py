from pathlib import Path
from typing import Final

from lexica.artifact.kind import ArtifactKind
from lexica.artifact.rescue import read_rescue_table, write_rescue_table
from lexica.artifact.words import read_word_list
from lexica.build.rescue import rescue_table_of
from lexica.lore.rescue import RescueTable
from lexica.names import DictionaryName
from lexica.sources.sgjp import build_morfeusz_engine
from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.lexicons import compile_dictionary
from wordtable.manifest import inputs_stand_recorded, record_inputs
from wordtable.paths import dictionary_compiled
from wordtable.releases import POLIMORF_RELEASE

_NO_RESCUE: Final[RescueTable] = {}


def rescue_path(name: DictionaryName) -> Path:
    return dictionary_compiled(name, ArtifactKind.RESCUE)


def load_rescue(name: DictionaryName) -> RescueTable:
    path = rescue_path(name)
    if not path.is_file():
        return _NO_RESCUE

    return read_rescue_table(path)


def compile_rescue(name: DictionaryName, polimorf_path: Path) -> Path:
    destination = rescue_path(name)
    if destination.is_file() and inputs_stand_recorded(name, polimorf_path):
        return destination

    _ensure_polimorf_present(polimorf_path)
    lexicon = read_word_list(compile_dictionary(name))
    table = rescue_table_of(lexicon.words, build_morfeusz_engine(), polimorf_path)
    write_rescue_table(table, destination)
    record_inputs(name, polimorf_path)
    return destination


def _ensure_polimorf_present(polimorf_path: Path) -> None:
    if not polimorf_path.is_file():
        raise InvalidConfiguration(
            f"the rescue build reads the PoliMorf table at {polimorf_path}; "
            f"run 'wordtable fetch' to download {POLIMORF_RELEASE.url}"
        )
