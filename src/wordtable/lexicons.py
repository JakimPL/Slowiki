import asyncio
from pathlib import Path

from lexica.compile import compile_lexicon, load_compiled_lexicon
from lexica.dictionaries.catalog import iter_dictionary_words
from lexica.names import DictionaryName
from wordcore.lexicon.protocol import Lexicon
from wordtable.paths import dictionary_archive, dictionary_compiled


def dictionary_ready(name: DictionaryName) -> bool:
    return dictionary_compiled(name).is_file() or dictionary_archive(name).is_file()


def compile_dictionary(name: DictionaryName) -> Path:
    archive = dictionary_archive(name)
    compiled = dictionary_compiled(name)
    if not compiled.is_file():
        compile_lexicon(iter_dictionary_words(name, archive), compiled)

    return compiled


def load_lexicon(name: DictionaryName) -> Lexicon:
    return load_compiled_lexicon(compile_dictionary(name))


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
