import zipfile
from typing import Final

_README_NAME: Final = "readme.txt"


def word_list_members(bundle: zipfile.ZipFile) -> list[str]:
    candidates = [name for name in bundle.namelist() if name.endswith(".txt")]
    return [name for name in candidates if name.lower() != _README_NAME]


def decode_word_line(raw: bytes) -> str:
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return raw.decode("iso-8859-2").strip()
