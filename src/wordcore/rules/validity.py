from wordcore.exceptions import InvalidWord
from wordcore.lexicon.lexicon import Lexicon
from wordcore.rules.words import FormedWord


def validate_words(lexicon: Lexicon, words: tuple[FormedWord, ...], validate: bool) -> None:
    if not validate:
        return
    invalid = [word.text for word in words if not lexicon.judge(word.text).allowed]
    if invalid:
        raise InvalidWord("invalid words: " + ", ".join(invalid))
