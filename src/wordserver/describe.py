from wordcore.tiles.tile import Letter
from wordcore.tiles.tileset import TileSet
from wordserver.models.rule_parameters import RuleParameters
from wordserver.models.table_description import TableDescription
from wordserver.models.table_meta import TableMeta
from wordtable.lexicons import dictionary_ready
from wordtable.lore import lore_ready
from wordtable.rules import RulesConfig
from wordtable.timing import TimeConfig


def word_check_offered(rules: RulesConfig) -> bool:
    return rules.validate_on_play and dictionary_ready(rules.dictionary)


def lore_offered(rules: RulesConfig) -> bool:
    return lore_ready(rules.dictionary)


def table_description(
    meta: TableMeta,
    observer: int | None,
) -> TableDescription:
    resolved = meta.resolved
    rules = resolved.rules
    return TableDescription(
        code=meta.code if observer is not None else None,
        scheme=resolved.scheme,
        seats=rules.seats,
        dictionary=rules.dictionary,
        parameters=_rule_parameters(rules, meta.time),
        alphabet=_alphabet(resolved.tiles),
        distribution=_distribution(resolved.tiles),
        blanks=resolved.tiles.blanks,
    )


def _rule_parameters(
    rules: RulesConfig,
    time: TimeConfig,
) -> RuleParameters:
    return RuleParameters(
        rack_size=rules.rack_size,
        exchange_limit=rules.exchange_limit,
        exchange_min_bag=rules.exchange_min_bag,
        pass_allowed=rules.pass_allowed,
        bingo_bonus=rules.bingo_bonus,
        validate_on_play=rules.validate_on_play,
        word_check=word_check_offered(rules),
        lore=lore_offered(rules),
        premoves_allowed=rules.premoves,
        pass_end_rounds=rules.pass_end_rounds,
        scoreless_end_limit=rules.scoreless_end_limit,
        time=time,
    )


def _alphabet(tiles: TileSet) -> tuple[Letter, ...]:
    return tuple(
        Letter(
            symbol=spec.symbol,
            value=spec.value,
            category=spec.category,
        )
        for spec in tiles.letters
    )


def _distribution(tiles: TileSet) -> dict[str, int]:
    return {spec.symbol: spec.count for spec in tiles.letters}
