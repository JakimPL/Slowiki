from typing import ClassVar

from wordgames.backend.base import WordGameRules
from wordgames.names import GameName


class ScrabbleRules(WordGameRules):
    game_name: ClassVar[GameName] = GameName.SCRABBLE
