from wordcore.board.preset import board_from_preset
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.games.rules import Rules
from wordcore.lexicon.protocol import Lexicon
from wordgames.backend.literaki import LiterakiRules
from wordgames.backend.parameters import GameParameters
from wordgames.backend.scrabble import ScrabbleRules
from wordgames.names import GameName
from wordtable.catalog import ResolvedScheme


def build_rules(
    resolved: ResolvedScheme,
    players: tuple[int, ...],
    lexicon: Lexicon,
) -> Rules:
    board = board_from_preset(resolved.board)
    parameters = GameParameters(
        validate_on_play=resolved.scheme.validate_on_play,
        exchange_limit=resolved.scheme.exchange_limit,
        exchange_min_bag=resolved.scheme.exchange_min_bag,
        pass_allowed=resolved.scheme.pass_allowed,
        pass_end_limit=resolved.scheme.pass_end_limit,
        scoreless_end_limit=resolved.scheme.scoreless_end_limit,
        bingo_bonus=resolved.scheme.bingo_bonus,
    )

    match resolved.scheme.game:
        case GameName.LITERAKI:
            return LiterakiRules(
                players,
                board,
                resolved.tiles,
                lexicon,
                parameters,
            )

        case GameName.SCRABBLE:
            return ScrabbleRules(
                players,
                board,
                resolved.tiles,
                lexicon,
                parameters,
            )

        case _:
            raise InvalidConfiguration(f"unknown game: {resolved.scheme.game}")
