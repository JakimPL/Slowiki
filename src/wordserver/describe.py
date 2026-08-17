from wordcore.tiles.tile import Letter, TilePreset
from wordserver.models import RuleParameters, TableDescription
from wordserver.registry import TableMeta
from wordtable.config import SchemeConfig


def table_description(meta: TableMeta, observer: int | None) -> TableDescription:
    scheme = meta.resolved.scheme
    tiles = meta.resolved.tiles
    return TableDescription(
        code=meta.code if observer is not None else None,
        scheme=meta.scheme,
        game=meta.game,
        seats=meta.max_players,
        dictionary=scheme.dictionary,
        parameters=_rule_parameters(scheme, tiles),
        alphabet=_alphabet(tiles),
        distribution=_distribution(tiles),
        blanks=tiles.blanks,
    )


def _rule_parameters(scheme: SchemeConfig, tiles: TilePreset) -> RuleParameters:
    return RuleParameters(
        rack_size=tiles.rack_size,
        exchange_limit=scheme.exchange_limit,
        exchange_min_bag=scheme.exchange_min_bag,
        pass_allowed=scheme.pass_allowed,
        bingo_bonus=scheme.bingo_bonus,
        validate_on_play=scheme.validate_on_play,
        premoves_allowed=scheme.premoves,
        pass_end_limit=scheme.pass_end_limit,
        scoreless_end_limit=scheme.scoreless_end_limit,
        time=scheme.time,
    )


def _alphabet(tiles: TilePreset) -> tuple[Letter, ...]:
    return tuple(
        Letter(symbol=spec.symbol, value=spec.value, category=spec.category)
        for spec in tiles.letters
    )


def _distribution(tiles: TilePreset) -> dict[str, int]:
    return {spec.symbol: spec.count for spec in tiles.letters}
