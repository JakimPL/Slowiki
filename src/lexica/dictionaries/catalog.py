from collections.abc import Iterator
from pathlib import Path

from lexica.dictionaries.plain import iter_plain_words
from lexica.dictionaries.sjp import iter_sjp_words
from lexica.names import DictionaryName


def iter_dictionary_words(name: DictionaryName, archive: Path) -> Iterator[str]:
    match name:
        case DictionaryName.SJP:
            return iter_sjp_words(archive)
        case DictionaryName.OSPS | DictionaryName.ENGLISH:
            return iter_plain_words(archive)
