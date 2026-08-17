import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Final

from lexica.dictionaries.bundles import decode_word_line, word_list_members
from wordcore.exceptions import InvalidConfiguration

_SJP_FILENAME: Final = "slowa.txt"


def iter_sjp_words(archive: Path) -> Iterator[str]:
    with zipfile.ZipFile(archive) as bundle:
        word_lists = word_list_members(bundle)
        if _SJP_FILENAME not in word_lists:
            raise InvalidConfiguration(f"no word list '{_SJP_FILENAME}' found in {archive}")

        with bundle.open(_SJP_FILENAME) as handle:
            for raw in handle:
                word = decode_word_line(raw)
                if word:
                    yield word.upper()
