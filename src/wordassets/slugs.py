from typing import Final

_DIACRITICS: Final = {
    "Ą": "a-ogonek",
    "Ć": "c-acute",
    "Ę": "e-ogonek",
    "Ł": "l-stroke",
    "Ń": "n-acute",
    "Ó": "o-acute",
    "Ś": "s-acute",
    "Ź": "z-acute",
    "Ż": "z-dot",
}


def letter_slug(letter: str) -> str:
    if letter in _DIACRITICS:
        return _DIACRITICS[letter]

    if letter.isascii() and letter.isalnum():
        return letter.lower()

    return f"u-{ord(letter):04x}"
