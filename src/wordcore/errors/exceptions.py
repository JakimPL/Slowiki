class WordcoreError(Exception):
    pass


class IllegalMove(WordcoreError):
    pass


class NotYourTurn(WordcoreError):
    pass


class StalePosition(WordcoreError):
    pass


class InvalidWord(WordcoreError):
    pass


class GameOver(WordcoreError):
    pass


class InvalidConfiguration(WordcoreError):
    pass


class MissingConfiguration(InvalidConfiguration):
    pass


class NoPremove(WordcoreError):
    pass
