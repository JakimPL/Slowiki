from wordcore.tiles.tile import Letter
from wordcore.tiles.tileset import TileSet
from wordserver.models.feedback import FeedbackOffered
from wordserver.models.table_description import TableDescription
from wordserver.models.table_meta import TableMeta
from wordtable.lexicons import dictionary_ready
from wordtable.lore import lore_ready
from wordtable.rules import RulesConfig


def word_check_offered(rules: RulesConfig) -> bool:
    return rules.validate_on_play and dictionary_ready(rules.dictionary)


def lore_offered(rules: RulesConfig) -> bool:
    return lore_ready(rules.dictionary)


def table_description(
    meta: TableMeta,
    observer: int | None,
) -> TableDescription:
    resolved = meta.resolved
    return TableDescription(
        code=meta.code if observer is not None else None,
        scheme=resolved.scheme,
        specimen=resolved.specimen,
        rules=resolved.rules,
        feedback=_feedback(resolved.rules),
        alphabet=_alphabet(resolved.tiles),
        distribution=_distribution(resolved.tiles),
        blanks=resolved.tiles.blanks,
    )


def _feedback(rules: RulesConfig) -> FeedbackOffered:
    return FeedbackOffered(
        word_check=word_check_offered(rules),
        lore=lore_offered(rules),
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
