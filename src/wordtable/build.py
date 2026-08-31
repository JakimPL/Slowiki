from wordcore.board.preset import board_from_preset
from wordcore.games.rules import Rules
from wordcore.lexicon.protocol import Lexicon
from wordgames.backend.base import WordGameRules
from wordgames.backend.parameters import GameParameters
from wordtable.resolved import ResolvedScheme


def build_rules(
    resolved: ResolvedScheme,
    players: tuple[int, ...],
    lexicon: Lexicon,
) -> Rules:
    rules = resolved.rules
    parameters = GameParameters(
        rack_size=rules.rack_size,
        validate_on_play=rules.validate_on_play,
        exchange_limit=rules.exchange_limit,
        exchange_min_bag=rules.exchange_min_bag,
        pass_allowed=rules.pass_allowed,
        pass_end_rounds=rules.pass_end_rounds,
        scoreless_end_limit=rules.scoreless_end_limit,
        bingo_bonus=rules.bingo_bonus,
    )
    return WordGameRules(
        players,
        board_from_preset(resolved.board),
        resolved.tiles,
        lexicon,
        parameters,
    )
