import asyncio

from lexica.compile import compile_lexicon, load_compiled_lexicon
from lexica.names import DictionaryName
from lexica.sjp import iter_sjp_words
from wordcore.lexicon.lexicon import Lexicon
from wordtable.paths import dictionary_archive, dictionary_compiled


def load_lexicon(name: DictionaryName) -> Lexicon:
    archive = dictionary_archive(name)
    compiled = dictionary_compiled(name)
    if not compiled.is_file():
        compile_lexicon(iter_sjp_words(archive), compiled)
    return load_compiled_lexicon(compiled)


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
