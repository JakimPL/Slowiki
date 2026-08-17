import zipfile
from collections.abc import Iterator
from pathlib import Path

from lexica.dictionaries.bundles import decode_word_line, word_list_members
from wordcore.errors.exceptions import InvalidConfiguration


def iter_plain_words(archive: Path) -> Iterator[str]:
    with zipfile.ZipFile(archive) as bundle:
        word_lists = word_list_members(bundle)
        if not word_lists:
            raise InvalidConfiguration(f"no word lists found in {archive}")

        for member in sorted(word_lists):
            yield from _member_words(bundle, member)


def _member_words(bundle: zipfile.ZipFile, member: str) -> Iterator[str]:
    with bundle.open(member) as handle:
        for raw in handle:
            word = decode_word_line(raw)
            if word:
                yield word.upper()
