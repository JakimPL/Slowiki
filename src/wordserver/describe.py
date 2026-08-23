from wordcore.tiles.tile import Letter, TilePreset
from wordserver.models.rule_parameters import RuleParameters
from wordserver.models.table_description import TableDescription
from wordserver.models.table_meta import TableMeta
from wordtable.config import SchemeConfig, TimeConfig
from wordtable.lexicons import dictionary_ready
from wordtable.lore import lore_ready


def word_check_offered(scheme: SchemeConfig) -> bool:
    return scheme.validate_on_play and dictionary_ready(scheme.dictionary)


def lore_offered(scheme: SchemeConfig) -> bool:
    return lore_ready(scheme.dictionary)


def table_description(
    meta: TableMeta,
    observer: int | None,
) -> TableDescription:
    scheme = meta.resolved.scheme
    tiles = meta.resolved.tiles
    return TableDescription(
        code=meta.code if observer is not None else None,
        scheme=meta.scheme,
        game=meta.game,
        seats=meta.max_players,
        dictionary=scheme.dictionary,
        parameters=_rule_parameters(scheme, tiles, meta.time),
        alphabet=_alphabet(tiles),
        distribution=_distribution(tiles),
        blanks=tiles.blanks,
    )


def _rule_parameters(
    scheme: SchemeConfig,
    tiles: TilePreset,
    time: TimeConfig,
) -> RuleParameters:
    return RuleParameters(
        rack_size=tiles.rack_size,
        exchange_limit=scheme.exchange_limit,
        exchange_min_bag=scheme.exchange_min_bag,
        pass_allowed=scheme.pass_allowed,
        bingo_bonus=scheme.bingo_bonus,
        validate_on_play=scheme.validate_on_play,
        word_check=word_check_offered(scheme),
        lore=lore_offered(scheme),
        premoves_allowed=scheme.premoves,
        pass_end_rounds=scheme.pass_end_rounds,
        scoreless_end_limit=scheme.scoreless_end_limit,
        time=time,
    )


def _alphabet(tiles: TilePreset) -> tuple[Letter, ...]:
    return tuple(
        Letter(
            symbol=spec.symbol,
            value=spec.value,
            category=spec.category,
        )
        for spec in tiles.letters
    )


def _distribution(tiles: TilePreset) -> dict[str, int]:
    return {spec.symbol: spec.count for spec in tiles.letters}
