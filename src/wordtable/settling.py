from pathlib import Path

from wordcore.board.preset import BoardPreset
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.tiles.blank import BLANK_CATEGORY
from wordcore.tiles.tileset import TileSet
from wordtable.allowances.load import load_allowances
from wordtable.limits import ensure_within_limits
from wordtable.presets.alphabet import AlphabetPreset
from wordtable.presets.letters import letters_of
from wordtable.presets.load import (
    load_alphabet_preset,
    load_board_preset,
    load_distribution_preset,
)
from wordtable.resolved import ResolvedScheme
from wordtable.rules import RulesConfig
from wordtable.scheme import SchemeConfig


def resolve_table(
    directory: Path,
    scheme: SchemeConfig,
    asked: RulesConfig | None,
) -> ResolvedScheme:
    rules = scheme.rules if asked is None else asked
    ensure_within_limits(rules, load_allowances(directory))
    _ensure_the_rules_agree(rules)
    board = load_board_preset(directory, rules.board)
    alphabet = load_alphabet_preset(directory, rules.alphabet)
    tiles = _tiles_of(directory, alphabet, rules)
    _ensure_the_alphabet_admits_the_dictionary(alphabet, rules)
    _ensure_every_painted_category_is_carried(board, tiles)
    _ensure_the_bag_fills_every_rack(tiles, rules)
    _ensure_the_opening_fits_the_board(board, rules)
    return ResolvedScheme(
        scheme=scheme.name,
        specimen=scheme.specimen,
        rules=rules,
        board=board,
        tiles=tiles,
    )


def seats_admitted(tiles: TileSet, rack_size: int | None) -> int:
    if rack_size is None:
        return 1

    return tiles.total() // rack_size


def _ensure_the_rules_agree(rules: RulesConfig) -> None:
    _ensure_an_end_limit(rules)
    _ensure_one_seat_holds_the_whole_bag(rules)
    _ensure_a_bingo_fits_the_rack(rules)
    _ensure_the_rack_can_open(rules)
    _ensure_the_blank_keeps_its_category(rules)


def _ensure_an_end_limit(rules: RulesConfig) -> None:
    if rules.seats > 1 and rules.pass_end_rounds is None and rules.scoreless_end_limit is None:
        raise InvalidConfiguration(
            "a table seating several players needs pass_end_rounds or scoreless_end_limit"
        )


def _ensure_one_seat_holds_the_whole_bag(rules: RulesConfig) -> None:
    if rules.rack_size is None and rules.seats > 1:
        raise InvalidConfiguration("a table dealing the whole bag seats one player")


def _ensure_a_bingo_fits_the_rack(rules: RulesConfig) -> None:
    if rules.bingo_tiles is None or rules.rack_size is None:
        return

    if rules.bingo_tiles > rules.rack_size:
        raise InvalidConfiguration(
            f"a bingo of {rules.bingo_tiles} tiles overruns a rack of {rules.rack_size}"
        )


def _ensure_the_rack_can_open(rules: RulesConfig) -> None:
    if rules.rack_size is not None and rules.opening_tiles > rules.rack_size:
        raise InvalidConfiguration(
            f"an opening word of {rules.opening_tiles} tiles overruns "
            f"a rack of {rules.rack_size}"
        )


def _ensure_the_blank_keeps_its_category(rules: RulesConfig) -> None:
    claimed = sorted(
        symbol
        for symbol, adjustment in rules.letters.items()
        if adjustment.category == BLANK_CATEGORY
    )
    if claimed:
        raise InvalidConfiguration(
            f"the category '{BLANK_CATEGORY}' belongs to blank tiles, "
            f"and {''.join(claimed)} claims it"
        )


def _tiles_of(
    directory: Path,
    alphabet: AlphabetPreset,
    rules: RulesConfig,
) -> TileSet:
    distribution = load_distribution_preset(directory, rules.distribution)
    return TileSet(
        letters=letters_of(alphabet, distribution, rules.letters),
        blanks=rules.blanks,
    )


def _ensure_the_alphabet_admits_the_dictionary(
    alphabet: AlphabetPreset,
    rules: RulesConfig,
) -> None:
    if rules.dictionary not in alphabet.dictionaries:
        admitted = ", ".join(sorted(alphabet.dictionaries))
        raise InvalidConfiguration(
            f"alphabet '{alphabet.name}' admits {admitted}, and this table asks "
            f"for '{rules.dictionary}'"
        )


def _ensure_every_painted_category_is_carried(board: BoardPreset, tiles: TileSet) -> None:
    carried = {spec.category for spec in tiles.letters} | {BLANK_CATEGORY}
    painted = {bonus.category for bonus in board.bonuses if bonus.category is not None}
    unknown = ", ".join(sorted(painted - carried))
    if unknown:
        raise InvalidConfiguration(
            f"board '{board.name}' paints {unknown}, which no letter carries"
        )


def _ensure_the_bag_fills_every_rack(tiles: TileSet, rules: RulesConfig) -> None:
    admitted = seats_admitted(tiles, rules.rack_size)
    if rules.seats > admitted:
        raise InvalidConfiguration(
            f"a bag of {tiles.total()} tiles seats {admitted} at {rules.rack_size} "
            f"tiles a rack, and this table asks for {rules.seats}"
        )


def _ensure_the_opening_fits_the_board(board: BoardPreset, rules: RulesConfig) -> None:
    if rules.opening_tiles > board.size:
        raise InvalidConfiguration(
            f"an opening word of {rules.opening_tiles} tiles overruns "
            f"board '{board.name}' at {board.size}"
        )
