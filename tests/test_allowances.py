from typing import Final

import pytest
from pydantic import ValidationError

from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.allowances.allowance import Allowance
from wordtable.allowances.bounds import SETTING_BOUNDS
from wordtable.allowances.catalog import AllowanceCatalog
from wordtable.allowances.choices import offered_choices
from wordtable.allowances.kind import SettingKind
from wordtable.allowances.load import load_allowances
from wordtable.allowances.name import SettingName
from wordtable.catalog import list_schemes
from wordtable.documents import read_mapping
from wordtable.paths import CONFIG_DIR, CONFIGURATION_ALLOWANCES_FILE
from wordtable.rules import RulesConfig, restated
from wordtable.scheme import load_scheme

BOUNDS_ARE_CODE: Final = frozenset({"minimum", "maximum", "step", "unlimited", "offered_values"})
NUMERIC_KINDS: Final = frozenset(
    {SettingKind.COUNT, SettingKind.OPTIONAL_COUNT, SettingKind.SECONDS}
)
CHOICE_SETTINGS: Final = (
    SettingName.BOARD,
    SettingName.ALPHABET,
    SettingName.DISTRIBUTION,
)


def catalog() -> AllowanceCatalog:
    return load_allowances(CONFIG_DIR)


def unconstrained() -> RulesConfig:
    return restated(
        load_scheme(CONFIG_DIR, "literaki").rules,
        {
            "seats": 1,
            "rack_size": 15,
            "opening_tiles": 1,
            "bingo_tiles": None,
        },
    )


def stated(setting: SettingName, value: object) -> RulesConfig:
    return restated(unconstrained(), {setting.value: value})


def test_every_setting_names_a_field_of_the_record() -> None:
    assert {setting.value for setting in SettingName} == set(RulesConfig.model_fields)


def test_every_setting_carries_one_allowance() -> None:
    by_setting = catalog().by_setting()
    assert set(by_setting) == set(SettingName)


def test_a_catalog_leaving_a_setting_out_names_it() -> None:
    kept = tuple(
        allowance for allowance in catalog().allowances if allowance.setting != SettingName.SEATS
    )
    with pytest.raises(InvalidConfiguration, match="leave seats undescribed"):
        AllowanceCatalog(allowances=kept)


def test_a_catalog_stating_a_setting_twice_names_it() -> None:
    allowances = catalog().allowances
    with pytest.raises(InvalidConfiguration, match="state seats more than once"):
        AllowanceCatalog(allowances=allowances + (allowances[0],))


def test_the_catalog_declares_no_bounds() -> None:
    assert BOUNDS_ARE_CODE.isdisjoint(Allowance.model_fields)
    for row in read_mapping(CONFIG_DIR / CONFIGURATION_ALLOWANCES_FILE)["allowances"]:
        assert BOUNDS_ARE_CODE.isdisjoint(row)


def test_every_numeric_setting_states_its_bounds() -> None:
    numeric = {
        allowance.setting for allowance in catalog().allowances if allowance.kind in NUMERIC_KINDS
    }
    assert numeric == set(SETTING_BOUNDS)


@pytest.mark.parametrize("setting", sorted(SETTING_BOUNDS))
def test_each_bound_is_the_one_the_record_enforces(setting: SettingName) -> None:
    bounds = SETTING_BOUNDS[setting]
    assert getattr(stated(setting, bounds.minimum), setting.value) == bounds.minimum
    assert getattr(stated(setting, bounds.maximum), setting.value) == bounds.maximum
    with pytest.raises(ValidationError):
        stated(setting, bounds.minimum - 1)

    with pytest.raises(ValidationError):
        stated(setting, bounds.maximum + 1)


@pytest.mark.parametrize("setting", sorted(SETTING_BOUNDS))
def test_a_setting_takes_no_value_only_where_the_bounds_say_so(setting: SettingName) -> None:
    if SETTING_BOUNDS[setting].unlimited:
        assert getattr(stated(setting, None), setting.value) is None
        return

    with pytest.raises(ValidationError):
        stated(setting, None)


def test_every_rung_is_a_value_the_record_accepts() -> None:
    for allowance in catalog().allowances:
        if allowance.offered is None:
            continue

        bounds = SETTING_BOUNDS[allowance.setting]
        for rung in allowance.offered:
            assert bounds.minimum <= rung <= bounds.maximum
            assert getattr(stated(allowance.setting, rung), allowance.setting.value) == rung


def test_every_clock_setting_offers_rungs() -> None:
    by_setting = catalog().by_setting()
    for setting, allowance in by_setting.items():
        if allowance.kind == SettingKind.SECONDS:
            assert allowance.offered
        else:
            assert allowance.offered is None, setting


def test_the_offered_choices_read_what_is_on_disk() -> None:
    choices = offered_choices(CONFIG_DIR)
    assert choices[SettingName.BOARD] == ("literaki", "scrabble")
    assert choices[SettingName.ALPHABET] == ("literaki", "scrabble-en", "scrabble-pl")
    assert choices[SettingName.DISTRIBUTION] == ("english", "polish")
    assert set(choices[SettingName.DICTIONARY]) <= {name.value for name in DictionaryName}


def test_every_scheme_holds_an_offered_value_for_every_choice() -> None:
    choices = offered_choices(CONFIG_DIR)
    for scheme in list_schemes(CONFIG_DIR).values():
        for setting in CHOICE_SETTINGS:
            assert getattr(scheme.rules, setting.value) in choices[setting]
