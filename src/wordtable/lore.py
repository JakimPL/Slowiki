import asyncio

from lexica.lore.lookup import lore_of
from lexica.lore.reading import WordLore
from lexica.lore.sources import LoreSources
from lexica.names import DictionaryName
from lexica.sources.coverage import morphology_covers
from lexica.sources.sgjp import MorfeuszEngine, build_morfeusz_engine, morphology_available
from wordcore.lexicon.protocol import Lexicon
from wordtable.lexicons import LexiconService, dictionary_ready
from wordtable.rescue import load_rescue


def lore_ready(name: DictionaryName) -> bool:
    return morphology_available() and morphology_covers(name) and dictionary_ready(name)


class LoreService:
    def __init__(self, lexicons: LexiconService) -> None:
        self._lexicons = lexicons
        self._engine: MorfeuszEngine | None = None
        self._sources: dict[DictionaryName, LoreSources] = {}
        self._lock = asyncio.Lock()

    async def read(self, name: DictionaryName, words: tuple[str, ...]) -> dict[str, WordLore]:
        lexicon = await self._lexicons.get(name)
        async with self._lock:
            sources = await self._prepared(name)
            return await asyncio.to_thread(_read_words, sources, words, lexicon)

    async def prepare(self, name: DictionaryName) -> None:
        async with self._lock:
            await self._prepared(name)

    async def _prepared(self, name: DictionaryName) -> LoreSources:
        standing = self._sources.get(name)
        if standing is not None:
            return standing

        engine = await self._engine_ready()
        rescue = await asyncio.to_thread(load_rescue, name)
        sources = LoreSources(engine=engine, rescue=rescue)
        self._sources[name] = sources
        return sources

    async def _engine_ready(self) -> MorfeuszEngine:
        if self._engine is None:
            self._engine = await asyncio.to_thread(build_morfeusz_engine)

        return self._engine


def _read_words(
    sources: LoreSources,
    words: tuple[str, ...],
    lexicon: Lexicon,
) -> dict[str, WordLore]:
    return {word: lore_of(sources, word, lexicon) for word in words}
