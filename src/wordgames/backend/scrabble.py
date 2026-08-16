from typing import ClassVar

from wordgames.backend.base import WordGameRules


class ScrabbleRules(WordGameRules):
    game_name: ClassVar[str] = "scrabble"
