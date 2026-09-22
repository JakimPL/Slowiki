import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Final

from lexica.dictionaries.bundles import decode_word_line, word_list_members
from wordcore.errors.exceptions import InvalidConfiguration

SJP_WORD_LIST: Final = "slowa.txt"


def iter_sjp_words(archive: Path) -> Iterator[str]:
    with zipfile.ZipFile(archive) as bundle:
        word_lists = word_list_members(bundle)
        if SJP_WORD_LIST not in word_lists:
            raise InvalidConfiguration(f"no word list '{SJP_WORD_LIST}' found in {archive}")

        with bundle.open(SJP_WORD_LIST) as handle:
            for raw in handle:
                word = decode_word_line(raw)
                if word:
                    yield word.upper()
