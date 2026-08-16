import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Final

from wordcore.exceptions import InvalidConfiguration

_SJP_FILENAME: Final = "slowa.txt"


def get_word_filenames(bundle: zipfile.ZipFile) -> list[str]:
    names = [name for name in bundle.namelist() if name.endswith(".txt")]
    return [name for name in names if name.lower() != "readme.txt"]


def iter_sjp_words(archive: Path) -> Iterator[str]:
    with zipfile.ZipFile(archive) as bundle:
        word_lists = get_word_filenames(bundle)
        if _SJP_FILENAME not in word_lists:
            raise InvalidConfiguration(f"no word list '{_SJP_FILENAME}' found in {archive}")

        with bundle.open(_SJP_FILENAME) as handle:
            for raw in handle:
                word = _decode_line(raw)
                if word:
                    yield word.upper()


def _decode_line(raw: bytes) -> str:
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return raw.decode("iso-8859-2").strip()
