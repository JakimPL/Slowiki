from wordbots.bot import Bot


class BotRegistry:
    def __init__(self) -> None:
        self._bots: dict[str, Bot] = {}

    def register(self, name: str, bot: Bot) -> None:
        self._bots[name] = bot

    def get(self, name: str) -> Bot:
        return self._bots[name]

    def names(self) -> tuple[str, ...]:
        return tuple(self._bots)
