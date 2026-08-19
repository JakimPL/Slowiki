from wordcore.errors.exceptions import InvalidWord
from wordcore.lexicon.protocol import Lexicon
from wordcore.rules.words.formed import FormedWord


def invalid_words(
    words: tuple[FormedWord, ...],
    lexicon: Lexicon,
    allowed_pos: tuple[str, ...] | None = None,
    base_form_only: bool = False,
) -> list[str]:
    invalid: list[str] = []
    for word in words:
        if not lexicon.judge(word.text).allowed:
            invalid.append(word.text)
            continue
        infos = lexicon.class_infos(word.text)
        if allowed_pos is not None and not any(info.part in allowed_pos for info in infos):
            invalid.append(word.text)
            continue
        if base_form_only and not any(info.base == word.text.upper() for info in infos):
            invalid.append(word.text)
    return invalid


def validate_words(
    lexicon: Lexicon,
    words: tuple[FormedWord, ...],
    validate: bool,
    allowed_pos: tuple[str, ...] | None = None,
    base_form_only: bool = False,
) -> None:
    if not validate:
        return

    invalid = invalid_words(words, lexicon, allowed_pos, base_form_only)
    if invalid:
        raise InvalidWord("invalid words: " + ", ".join(invalid))
