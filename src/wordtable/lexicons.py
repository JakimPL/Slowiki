import asyncio
from pathlib import Path

from lexica.artifact.kind import ArtifactKind
from lexica.artifact.words import read_word_list, write_word_list
from lexica.dictionaries.catalog import iter_dictionary_words
from lexica.names import DictionaryName
from wordcore.lexicon.protocol import Lexicon
from wordtable.paths import dictionary_archive, dictionary_compiled


def dictionary_ready(name: DictionaryName) -> bool:
    return word_list_path(name).is_file() or dictionary_archive(name).is_file()


def word_list_path(name: DictionaryName) -> Path:
    return dictionary_compiled(name, ArtifactKind.WORDS)


def compile_dictionary(name: DictionaryName) -> Path:
    archive = dictionary_archive(name)
    compiled = word_list_path(name)
    if not compiled.is_file():
        write_word_list(iter_dictionary_words(name, archive), compiled)

    return compiled


def load_lexicon(name: DictionaryName) -> Lexicon:
    return read_word_list(compile_dictionary(name))


class LexiconService:
    def __init__(self) -> None:
        self._cache: dict[DictionaryName, Lexicon] = {}

    async def get(self, name: DictionaryName) -> Lexicon:
        cached = self._cache.get(name)
        if cached is not None:
            return cached

        lexicon = await asyncio.to_thread(load_lexicon, name)
        self._cache[name] = lexicon
        return lexicon
