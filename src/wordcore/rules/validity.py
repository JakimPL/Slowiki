from wordcore.errors.exceptions import InvalidWord
from wordcore.lexicon.protocol import Lexicon
from wordcore.rules.words.formed import FormedWord


def invalid_words(
    words: tuple[FormedWord, ...],
    lexicon: Lexicon,
) -> list[str]:
    return [word.text for word in words if not lexicon.judge(word.text).allowed]


def validate_words(
    lexicon: Lexicon,
    words: tuple[FormedWord, ...],
    validate: bool,
) -> None:
    if not validate:
        return

    invalid = invalid_words(words, lexicon)
    if invalid:
        raise InvalidWord("invalid words: " + ", ".join(invalid))
