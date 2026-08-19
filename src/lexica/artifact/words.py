import marshal
from collections.abc import Iterable
from pathlib import Path

from lexica.artifact.envelope import read_envelope, write_envelope
from lexica.artifact.formats import ARTIFACT_FORMATS
from lexica.artifact.header import ArtifactHeader
from lexica.artifact.kind import ArtifactKind
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.lexicon.lexicon import TextLexicon


def write_word_list(words: Iterable[str], destination: Path) -> None:
    lexicon = TextLexicon.from_words(words)
    header = ArtifactHeader(
        kind=ArtifactKind.WORDS,
        format=ARTIFACT_FORMATS[ArtifactKind.WORDS],
        entries=len(lexicon.words),
    )
    write_envelope(destination, header, marshal.dumps(lexicon.words))


def read_word_list(path: Path) -> TextLexicon:
    header, body = read_envelope(path, ArtifactKind.WORDS)
    words = _decode_words(path, body)
    _ensure_entries(path, header, words)
    return TextLexicon(words=words)


def _decode_words(path: Path, body: bytes) -> tuple[str, ...]:
    try:
        decoded = marshal.loads(body)
    except (EOFError, ValueError) as error:
        raise InvalidConfiguration(
            f"{path} holds a damaged word list; delete the file and rebuild it"
        ) from error

    if not isinstance(decoded, tuple) or not all(isinstance(word, str) for word in decoded):
        raise InvalidConfiguration(f"{path} holds a word list of an unreadable shape")

    return decoded


def _ensure_entries(path: Path, header: ArtifactHeader, words: tuple[str, ...]) -> None:
    if len(words) != header.entries:
        raise InvalidConfiguration(
            f"{path} declares {header.entries} words and holds {len(words)}; "
            "delete the file and rebuild it"
        )
