from pathlib import Path

from lexica.compile import compile_lexicon, load_compiled_lexicon
from lexica.names import DictionaryName
from lexica.sjp import iter_sjp_words
from wordcore.exceptions import InvalidConfiguration
from wordcore.lexicon.lexicon import Lexicon


def load_lexicon(name: DictionaryName, dictionaries_dir: Path) -> Lexicon:
    match name:
        case DictionaryName.SJP:
            archive = dictionaries_dir / "sjp-20260803.zip"
            compiled = dictionaries_dir / "sjp-20260803.lexicon"
            if not compiled.is_file():
                compile_lexicon(iter_sjp_words(archive), compiled)
            return load_compiled_lexicon(compiled)
        case _:
            raise InvalidConfiguration(f"unknown dictionary: {name}")
