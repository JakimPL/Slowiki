from typing import ClassVar

from wordgames.backend.base import WordGameRules


class LiterakiRules(WordGameRules):
    game_name: ClassVar[str] = "literaki"
