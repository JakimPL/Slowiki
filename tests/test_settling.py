import random
import shutil
from pathlib import Path

import pytest

from lexica.names import DictionaryName
from wordcore.errors.exceptions import IllegalMove, InvalidConfiguration
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.moves.action import Play, PlayPlacement
from wordcore.moves.move import Move
from wordcore.positions.position import Position
from wordcore.rules.rack import rack_of
from wordtable.audit import audit_configuration
from wordtable.build import build_rules
from wordtable.catalog import list_schemes, offerings, resolve_scheme
from wordtable.paths import CONFIG_DIR
from wordtable.resolved import ResolvedScheme
from wordtable.rules import RulesConfig, restated
from wordtable.scheme import load_scheme
from wordtable.settling import resolve_table, seats_admitted
from wordtable.style import load_style_tokens
from wordtable.timing import time_of

TINY_BOARD = """size: 5
bonuses: []
"""


@pytest.fixture(name="tree")
def _tree(tmp_path: Path) -> Path:
    copied = tmp_path / "config"
    shutil.copytree(CONFIG_DIR, copied)
    return copied


def literaki_rules() -> RulesConfig:
    return load_scheme(CONFIG_DIR, "literaki").rules


def settled(tree: Path, changes: dict[str, object]) -> None:
    scheme = load_scheme(tree, "literaki")
    resolve_table(tree, scheme, restated(scheme.rules, changes))


def test_the_record_states_every_rule() -> None:
    stated = {name for name, field in RulesConfig.model_fields.items() if field.is_required()}
    assert stated == set(RulesConfig.model_fields)


def test_every_scheme_carries_a_complete_record() -> None:
    for name, scheme in list_schemes(CONFIG_DIR).items():
        assert scheme.name == name
        assert scheme.rules.seats >= 1


def test_the_polish_scrabble_scheme_plays_polish_letters_at_scrabble_values() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "scrabble-pl")
    by_symbol = {spec.symbol: spec for spec in resolved.tiles.letters}
    assert resolved.tiles.total() == 100
    assert {spec.category for spec in resolved.tiles.letters} == {"standard"}
    assert by_symbol["Ź"].value == 9
    assert by_symbol["Ź"].count == 1
    assert by_symbol["A"].value == 1
    assert by_symbol["A"].count == 9
    assert resolved.rules.board == "scrabble"
    assert resolved.rules.dictionary == DictionaryName.SJP


def test_the_settled_record_reaches_the_description() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    assert resolved.scheme == "literaki"
    assert resolved.specimen == "SŁOWIKI"
    assert resolved.rules.dictionary == DictionaryName.SJP
    assert resolved.rules.opening_tiles == 2
    assert resolved.rules.opening_covers_center is True
    assert resolved.rules.bingo_tiles is None
    assert resolved.rules.going_out_award is True


def test_the_clock_reads_the_record() -> None:
    rules = restated(literaki_rules(), {"per_turn_seconds": 90, "total_seconds": 600})
    assert time_of(rules).per_turn_seconds == 90
    assert time_of(rules).total_seconds == 600
    assert time_of(rules).increment_seconds == 0


def test_a_table_of_several_seats_needs_an_end_limit() -> None:
    with pytest.raises(InvalidConfiguration, match="pass_end_rounds"):
        restated(literaki_rules(), {"seats": 3, "pass_end_rounds": None})


def test_the_whole_bag_is_dealt_to_one_seat_only() -> None:
    with pytest.raises(InvalidConfiguration, match="whole bag"):
        restated(literaki_rules(), {"rack_size": None})


def test_a_bingo_fits_the_rack() -> None:
    assert restated(literaki_rules(), {"bingo_tiles": 6}).bingo_tiles == 6
    with pytest.raises(InvalidConfiguration, match="overruns a rack"):
        restated(literaki_rules(), {"bingo_tiles": 8})


def test_the_rack_holds_the_opening_word() -> None:
    with pytest.raises(InvalidConfiguration, match="opening word"):
        restated(literaki_rules(), {"opening_tiles": 9})


def test_no_letter_claims_the_blank_category() -> None:
    with pytest.raises(InvalidConfiguration, match="blank"):
        restated(literaki_rules(), {"letters": {"A": {"category": "blank"}}})


def test_a_symbol_is_adjusted_once() -> None:
    with pytest.raises(InvalidConfiguration, match="more than once"):
        restated(literaki_rules(), {"letters": {"a": {"value": 2}, "A": {"value": 3}}})


def test_a_setting_outside_its_bound_is_refused() -> None:
    for changes in ({"seats": 9}, {"bingo_bonus": 500}, {"rack_size": 40}, {"blanks": 99}):
        with pytest.raises(ValueError):
            restated(literaki_rules(), changes)


def test_a_preset_name_stays_a_preset_name() -> None:
    for name in ("../styles/default", "Literaki", "literaki.yaml", ""):
        with pytest.raises(ValueError):
            restated(literaki_rules(), {"board": name})


def test_the_alphabet_admits_the_dictionary(tree: Path) -> None:
    settled(tree, {"dictionary": "osps"})
    with pytest.raises(InvalidConfiguration, match="admits osps, sjp"):
        settled(tree, {"dictionary": "english"})


def test_the_board_paints_categories_the_letters_carry(tree: Path) -> None:
    with pytest.raises(InvalidConfiguration, match="which no letter carries"):
        settled(tree, {"alphabet": "scrabble-pl"})


def test_the_bag_fills_every_rack(tree: Path) -> None:
    with pytest.raises(InvalidConfiguration, match="asks for 8"):
        settled(tree, {"seats": 8, "rack_size": 15})


def test_the_opening_word_fits_the_board(tree: Path) -> None:
    (tree / "presets" / "boards" / "tiny.yaml").write_text(TINY_BOARD, encoding="utf-8")
    settled(tree, {"board": "tiny", "opening_tiles": 5})
    with pytest.raises(InvalidConfiguration, match="overruns board 'tiny'"):
        settled(tree, {"board": "tiny", "opening_tiles": 7})


def test_the_seats_a_bag_admits() -> None:
    tiles = resolve_scheme(CONFIG_DIR, "literaki").tiles
    assert seats_admitted(tiles, None) == 1
    assert seats_admitted(tiles, 7) == 8
    assert seats_admitted(tiles, 15) == 6
    assert seats_admitted(tiles, 200) == 0


def test_every_offering_carries_its_scheme_record() -> None:
    by_name = {offering.name: offering for offering in offerings(CONFIG_DIR)}
    assert by_name["literaki"].rules == load_scheme(CONFIG_DIR, "literaki").rules
    assert by_name["literaki"].specimen == "SŁOWIKI"
    assert by_name["solo-literaki"].rules.rack_size is None


def test_the_configuration_tree_audits_clean() -> None:
    audit_configuration(CONFIG_DIR)


def test_the_audit_names_a_scheme_reaching_a_preset_that_is_absent(tree: Path) -> None:
    scheme = (tree / "schemes" / "literaki.yaml").read_text(encoding="utf-8")
    (tree / "schemes" / "literaki.yaml").write_text(
        scheme.replace("board: literaki", "board: absent"),
        encoding="utf-8",
    )
    with pytest.raises(InvalidConfiguration, match="absent.yaml"):
        audit_configuration(tree)


def test_the_audit_reads_a_preset_no_scheme_names(tree: Path) -> None:
    (tree / "presets" / "alphabets" / "scrabble-pl.yaml").write_text(
        "order: AB\ndictionaries: [sjp]\nclasses:\n  - value: 1\n    letters: A\n",
        encoding="utf-8",
    )
    with pytest.raises(InvalidConfiguration, match="gives B no value"):
        audit_configuration(tree)


def repainted(tree: Path, specimen: str) -> None:
    path = tree / "schemes" / "literaki.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("specimen: SŁOWIKI", f"specimen: {specimen}"),
        encoding="utf-8",
    )


def test_the_audit_names_a_specimen_the_letters_cannot_spell(tree: Path) -> None:
    repainted(tree, "QUIZ")
    with pytest.raises(InvalidConfiguration, match="paints Q on its board art"):
        audit_configuration(tree)


def test_the_audit_names_a_specimen_wider_than_the_board(tree: Path) -> None:
    repainted(tree, "A" * 16)
    with pytest.raises(InvalidConfiguration, match="paints 16 letters"):
        audit_configuration(tree)


def test_a_theme_carries_a_band_for_every_category_a_scheme_paints() -> None:
    theme = load_style_tokens(CONFIG_DIR, "default").light
    for name in list_schemes(CONFIG_DIR):
        resolved = resolve_scheme(CONFIG_DIR, name)
        painted = {bonus.category for bonus in resolved.board.bonuses if bonus.category is not None}
        assert painted <= set(theme.tiles.bands)
        assert painted <= set(theme.category_premiums)


def test_the_opening_rules_a_table_states_reach_the_engine(tree: Path) -> None:
    scheme = load_scheme(tree, "literaki")
    standard = resolve_table(tree, scheme, None)
    off_centre = resolve_table(
        tree,
        scheme,
        restated(scheme.rules, {"opening_covers_center": False}),
    )
    wider = resolve_table(tree, scheme, restated(scheme.rules, {"opening_tiles": 3}))
    with pytest.raises(IllegalMove, match="center"):
        _opened(standard, row=0, column=0)

    _opened(off_centre, row=0, column=0)
    _opened(standard, row=7, column=7)
    with pytest.raises(IllegalMove, match="at least 3 tiles"):
        _opened(wider, row=7, column=7)


def _opened(resolved: ResolvedScheme, *, row: int, column: int) -> None:
    seats = tuple(range(resolved.rules.seats))
    position = _dealt(resolved, seats)
    tiles = [tile for tile in rack_of(position, 0) if not tile.blank][:2]
    word = "".join(tile.letter for tile in tiles)
    rules = build_rules(resolved, seats, TextLexicon.from_words([word]))
    placements = tuple(
        PlayPlacement(tile_id=tile.identifier, row=row, column=column + offset)
        for offset, tile in enumerate(tiles)
    )
    rules.validate(position, Move(player=0, action=Play(placements=placements)))


def _dealt(resolved: ResolvedScheme, seats: tuple[int, ...]) -> Position:
    lexicon = TextLexicon.from_words(["AA"])
    return build_rules(resolved, seats, lexicon).initial_position(random.Random(0))
