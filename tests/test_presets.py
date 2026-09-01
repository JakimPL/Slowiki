from pathlib import Path
from typing import Final

import pytest
import yaml
from pydantic import ValidationError

from lexica.names import DictionaryName
from wordcore.board.preset import BoardPreset
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.tiles.bag import build_tiles
from wordcore.tiles.tile import LetterSpec
from wordcore.tiles.tileset import TileSet
from wordtable.catalog import list_schemes, resolve_scheme
from wordtable.paths import CONFIG_DIR
from wordtable.presets.adjustment import LetterAdjustment
from wordtable.presets.alphabet import DEFAULT_CATEGORY, AlphabetPreset, LetterClass
from wordtable.presets.distribution import DistributionPreset
from wordtable.presets.letters import letters_of
from wordtable.presets.load import (
    load_alphabet_preset,
    load_distribution_preset,
)

RETIRED_TILE_PRESETS: Final = Path(__file__).resolve().parent / "specimens" / "tiles.yaml"
PRESET_PAIRS: Final = {
    "literaki": ("literaki", "polish"),
    "scrabble_pl": ("scrabble-pl", "polish"),
    "scrabble_en": ("scrabble-en", "english"),
}


def retired_letters() -> dict[str, list[dict[str, object]]]:
    return yaml.safe_load(RETIRED_TILE_PRESETS.read_text(encoding="utf-8"))


def spelled(letters: tuple[LetterSpec, ...]) -> list[dict[str, object]]:
    return [
        {
            "symbol": spec.symbol,
            "value": spec.value,
            "category": spec.category,
            "count": spec.count,
        }
        for spec in letters
    ]


def tiny_alphabet(**changes: object) -> dict[str, object]:
    return {
        "name": "tiny",
        "order": "AB",
        "dictionaries": ["sjp"],
        "classes": [{"value": 1, "category": "yellow", "letters": "AB"}],
        **changes,
    }


@pytest.mark.parametrize("preset", sorted(PRESET_PAIRS))
def test_preset_pairs_reproduce_the_retired_tile_presets(preset: str) -> None:
    alphabet_name, distribution_name = PRESET_PAIRS[preset]
    alphabet = load_alphabet_preset(CONFIG_DIR, alphabet_name)
    distribution = load_distribution_preset(CONFIG_DIR, distribution_name)
    assert spelled(letters_of(alphabet, distribution, {})) == retired_letters()[preset]


def test_every_scheme_resolves_a_hundred_tiles() -> None:
    for name in list_schemes(CONFIG_DIR):
        resolved = resolve_scheme(CONFIG_DIR, name)
        assert len(build_tiles(resolved.tiles)) == 100


def test_the_literaki_alphabet_admits_both_polish_lists() -> None:
    alphabet = load_alphabet_preset(CONFIG_DIR, "literaki")
    assert set(alphabet.dictionaries) == {DictionaryName.SJP, DictionaryName.OSPS}
    assert alphabet.order[:4] == ("A", "Ą", "B", "C")


def test_an_omitted_category_is_the_standard_one() -> None:
    alphabet = load_alphabet_preset(CONFIG_DIR, "scrabble-en")
    assert {letters.category for letters in alphabet.classes} == {DEFAULT_CATEGORY}


def test_letters_are_written_as_a_string_or_a_list() -> None:
    written = LetterClass(value=1, category="yellow", letters="ab")
    listed = LetterClass(value=1, category="yellow", letters=["a", "B"])
    assert written.letters == listed.letters == ("A", "B")


def test_an_alphabet_refuses_a_letter_it_never_values() -> None:
    with pytest.raises(InvalidConfiguration, match="gives C no value"):
        AlphabetPreset.model_validate(tiny_alphabet(order="ABC"))


def test_an_alphabet_refuses_a_value_it_never_orders() -> None:
    with pytest.raises(InvalidConfiguration, match="values unordered C"):
        AlphabetPreset.model_validate(
            tiny_alphabet(classes=[{"value": 1, "letters": "ABC"}]),
        )


def test_an_alphabet_refuses_two_values_for_one_letter() -> None:
    with pytest.raises(InvalidConfiguration, match="values B more than once"):
        AlphabetPreset.model_validate(
            tiny_alphabet(
                classes=[
                    {"value": 1, "letters": "AB"},
                    {"value": 2, "letters": "B"},
                ],
            ),
        )


def test_an_alphabet_refuses_a_repeated_order() -> None:
    with pytest.raises(InvalidConfiguration, match="orders A more than once"):
        AlphabetPreset.model_validate(tiny_alphabet(order="ABA"))


def test_a_distribution_refuses_two_counts_for_one_letter() -> None:
    with pytest.raises(InvalidConfiguration, match="counts A more than once"):
        DistributionPreset.model_validate({"name": "tiny", "counts": {1: "A", 2: "AB"}})


def test_a_distribution_covers_the_alphabet_both_ways() -> None:
    alphabet = AlphabetPreset.model_validate(tiny_alphabet())
    with pytest.raises(InvalidConfiguration, match="states no count for B"):
        letters_of(alphabet, DistributionPreset(name="short", counts={3: ("A",)}), {})

    with pytest.raises(InvalidConfiguration, match="counts C"):
        letters_of(alphabet, DistributionPreset(name="wide", counts={3: ("A", "B", "C")}), {})


def test_an_adjustment_changes_one_letter_and_leaves_the_rest() -> None:
    alphabet = load_alphabet_preset(CONFIG_DIR, "literaki")
    distribution = load_distribution_preset(CONFIG_DIR, "polish")
    letters = letters_of(alphabet, distribution, {"Ź": LetterAdjustment(value=12, count=3)})
    by_symbol = {spec.symbol: spec for spec in letters}
    assert by_symbol["Ź"] == LetterSpec(symbol="Ź", value=12, category="red", count=3)
    assert by_symbol["A"] == LetterSpec(symbol="A", value=1, category="yellow", count=9)


def test_an_adjustment_adds_a_letter_the_alphabet_lacks() -> None:
    alphabet = AlphabetPreset.model_validate(tiny_alphabet())
    distribution = DistributionPreset(name="tiny", counts={2: ("A", "B")})
    added = LetterAdjustment(value=7, category="blue", count=1)
    letters = letters_of(alphabet, distribution, {"C": added})
    assert letters[-1] == LetterSpec(symbol="C", value=7, category="blue", count=1)


def test_an_added_letter_states_all_three_of_its_facts() -> None:
    alphabet = AlphabetPreset.model_validate(tiny_alphabet())
    distribution = DistributionPreset(name="tiny", counts={2: ("A", "B")})
    with pytest.raises(InvalidConfiguration, match="lacks C"):
        letters_of(alphabet, distribution, {"C": LetterAdjustment(value=7)})


def test_an_empty_adjustment_is_refused() -> None:
    with pytest.raises(InvalidConfiguration, match="states a value, a category or a count"):
        LetterAdjustment()


def test_a_tile_set_refuses_a_repeated_letter() -> None:
    spec = LetterSpec(symbol="A", value=1, category="yellow", count=2)
    with pytest.raises(InvalidConfiguration, match="states A more than once"):
        TileSet(letters=(spec, spec), blanks=0)


def test_preset_numbers_stay_in_range() -> None:
    with pytest.raises(ValidationError):
        LetterClass(value=-1, category="yellow", letters="A")

    with pytest.raises(ValidationError):
        DistributionPreset(name="tiny", counts={100: ("A",)})

    with pytest.raises(ValidationError):
        LetterClass(value=1, category="yellow", letters="")


def test_a_board_preset_needs_an_odd_size_and_real_multipliers() -> None:
    with pytest.raises(InvalidConfiguration, match="odd size"):
        BoardPreset(name="even", size=16, bonuses=())

    with pytest.raises(ValidationError):
        BoardPreset(name="tiny", size=1, bonuses=())
