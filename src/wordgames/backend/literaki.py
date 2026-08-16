from typing import ClassVar

from wordgames.backend.base import WordGameRules
from wordgames.names import GameName


class LiterakiRules(WordGameRules):
    game_name: ClassVar[GameName] = GameName.LITERAKI
