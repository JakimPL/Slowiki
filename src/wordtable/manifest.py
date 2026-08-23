from pathlib import Path

from lexica.grammar.mapping_version import MAPPING_VERSION
from lexica.maintenance.manifest import (
    PIPELINE_VERSION,
    build_digests,
    load_manifest,
    write_manifest,
)
from lexica.names import DictionaryName
from lexica.sources.sgjp import SGJP_DICTIONARY
from wordtable.paths import dictionary_archive, dictionary_manifest


def build_inputs(name: DictionaryName, polimorf_path: Path) -> dict[str, str]:
    return build_digests(
        dictionary_archive(name),
        polimorf_path,
        SGJP_DICTIONARY,
        MAPPING_VERSION,
        PIPELINE_VERSION,
    )


def inputs_stand_recorded(name: DictionaryName, polimorf_path: Path) -> bool:
    archive = dictionary_archive(name)
    if not (archive.is_file() and polimorf_path.is_file()):
        return True

    return load_manifest(dictionary_manifest(name)) == build_inputs(name, polimorf_path)


def record_inputs(name: DictionaryName, polimorf_path: Path) -> None:
    write_manifest(dictionary_manifest(name), build_inputs(name, polimorf_path))
