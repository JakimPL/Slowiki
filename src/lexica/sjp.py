import zipfile
from collections.abc import Iterator
from pathlib import Path

from wordcore.exceptions import InvalidConfiguration


def iter_sjp_words(archive: Path) -> Iterator[str]:
    with zipfile.ZipFile(archive) as bundle:
        names = [name for name in bundle.namelist() if name.endswith(".txt")]
        word_lists = [name for name in names if name.lower() != "readme.txt"]
        if not word_lists:
            raise InvalidConfiguration(f"no word list found in {archive}")
        with bundle.open(word_lists[0]) as handle:
            for raw in handle:
                word = _decode_line(raw)
                if word:
                    yield word


def _decode_line(raw: bytes) -> str:
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return raw.decode("iso-8859-2").strip()
