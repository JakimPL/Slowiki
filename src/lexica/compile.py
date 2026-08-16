import marshal
from collections.abc import Iterable
from pathlib import Path

from wordcore.exceptions import InvalidConfiguration
from wordcore.lexicon.lexicon import TextLexicon


def compile_lexicon(words: Iterable[str], destination: Path) -> None:
    lexicon = TextLexicon.from_words(words)
    destination.write_bytes(marshal.dumps(lexicon.words))


def load_compiled_lexicon(path: Path) -> TextLexicon:
    data = marshal.loads(path.read_bytes())
    if not isinstance(data, tuple) or not all(isinstance(word, str) for word in data):
        raise InvalidConfiguration(f"malformed lexicon file: {path}")
    return TextLexicon(words=data)
