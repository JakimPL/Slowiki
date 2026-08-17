import asyncio
from pathlib import Path

from lexica.compile import compile_lexicon, compile_morph_lexicon, load_compiled_lexicon
from lexica.dictionaries.catalog import iter_dictionary_words
from lexica.dictionaries.sjp import iter_sjp_words
from lexica.morph.manifest import compile_input_digests, load_manifest, write_manifest
from lexica.morph.mapping import MAPPING_VERSION
from lexica.morph.overrides import parse_overrides
from lexica.morph.sources.sgjp import build_morfeusz_analyzer
from lexica.names import DictionaryName
from wordcore.lexicon.protocol import Lexicon
from wordtable.paths import (
    dictionary_archive,
    dictionary_compiled,
    lexicon_manifest,
    morph_overrides,
    polimorf_source,
)


def dictionary_ready(name: DictionaryName) -> bool:
    return dictionary_compiled(name).is_file() or dictionary_archive(name).is_file()


def compile_dictionary(name: DictionaryName) -> Path:
    archive = dictionary_archive(name)
    compiled = dictionary_compiled(name)
    if name is DictionaryName.SJP:
        _compile_sjp(archive, compiled)
    elif not compiled.is_file():
        compile_lexicon(iter_dictionary_words(name, archive), compiled)

    return compiled


def _compile_sjp(archive: Path, compiled: Path) -> None:
    source = polimorf_source()
    source_path = source if source.is_file() else None
    overrides_path = morph_overrides(DictionaryName.SJP)
    overrides_present = overrides_path.is_file()
    analyzer = build_morfeusz_analyzer()
    words = tuple(iter_sjp_words(archive))
    digests = compile_input_digests(
        archive,
        source_path,
        overrides_path if overrides_present else None,
        analyzer.dict_id(),
        MAPPING_VERSION,
    )
    manifest_path = lexicon_manifest(DictionaryName.SJP)
    if compiled.is_file() and load_manifest(manifest_path) == digests:
        return

    overrides = parse_overrides(overrides_path, frozenset(words)) if overrides_present else {}
    compile_morph_lexicon(words, analyzer, source_path, compiled, overrides)
    write_manifest(manifest_path, digests)


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
