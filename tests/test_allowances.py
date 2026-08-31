from typing import Final

import pytest
from pydantic import ValidationError

from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.allowances.allowance import Allowance
from wordtable.allowances.bounds import SettingBounds
from wordtable.allowances.catalog import AllowanceCatalog
from wordtable.allowances.choices import offered_choices
from wordtable.allowances.described import setting_allowances
from wordtable.allowances.group import SettingGroup
from wordtable.allowances.kind import BOUNDED_KINDS, SettingKind
from wordtable.allowances.load import load_allowances
from wordtable.allowances.name import SettingName
from wordtable.allowances.tier import SettingTier
from wordtable.catalog import list_schemes
from wordtable.documents import read_mapping
from wordtable.limits import SettingOutOfRange, ensure_within_limits
from wordtable.paths import CONFIG_DIR, CONFIGURATION_ALLOWANCES_FILE
from wordtable.resolved import ResolvedScheme
from wordtable.rules import RulesConfig, restated
from wordtable.scheme import load_scheme
from wordtable.settling import resolve_table

RANGE_FIELDS: Final = ("minimum", "maximum", "step")
WIDEST_RACK: Final = 15
CROWDED_RACK: Final = 7
CHOICE_SETTINGS: Final = (
    SettingName.BOARD,
    SettingName.ALPHABET,
    SettingName.DISTRIBUTION,
)


def catalog() -> AllowanceCatalog:
    return load_allowances(CONFIG_DIR)


def bounds_of(setting: SettingName) -> SettingBounds:
    bounds = catalog().by_setting()[setting].bounds()
    assert bounds is not None
    return bounds


def bounded() -> tuple[SettingName, ...]:
    return tuple(
        sorted(
            allowance.setting
            for allowance in catalog().allowances
            if allowance.bounds() is not None
        )
    )


def numbered() -> tuple[SettingName, ...]:
    return tuple(setting for setting in bounded() if setting is not SettingName.LETTERS)


def unconstrained() -> RulesConfig:
    return restated(
        load_scheme(CONFIG_DIR, "literaki").rules,
        {
            "seats": 1,
            "rack_size": WIDEST_RACK,
            "opening_tiles": 1,
            "bingo_tiles": None,
        },
    )


def base_for(setting: SettingName) -> RulesConfig:
    if setting is SettingName.SEATS:
        return restated(unconstrained(), {"rack_size": CROWDED_RACK})

    return unconstrained()


def stated(setting: SettingName, value: object) -> RulesConfig:
    return restated(base_for(setting), {setting.value: value})


def settled(setting: SettingName, value: object) -> ResolvedScheme:
    scheme = load_scheme(CONFIG_DIR, "literaki")
    return resolve_table(CONFIG_DIR, scheme, stated(setting, value))


def row(kind: SettingKind, **stated_fields: object) -> Allowance:
    return Allowance.model_validate(
        {
            "setting": SettingName.SEATS,
            "group": SettingGroup.TABLE,
            "tier": SettingTier.BASIC,
            "kind": kind,
            **stated_fields,
        }
    )


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


def test_the_catalog_states_the_range_of_every_bounded_setting() -> None:
    by_setting = catalog().by_setting()
    for setting, allowance in by_setting.items():
        assert (allowance.bounds() is not None) == (allowance.kind in BOUNDED_KINDS), setting


def test_the_authored_rows_carry_the_ranges() -> None:
    for authored in read_mapping(CONFIG_DIR / CONFIGURATION_ALLOWANCES_FILE)["allowances"]:
        allowance = Allowance.model_validate(authored)
        stated_fields = [field for field in RANGE_FIELDS if field in authored]
        assert bool(stated_fields) == (allowance.kind in BOUNDED_KINDS), authored


def test_a_bounded_kind_states_a_whole_range() -> None:
    with pytest.raises(InvalidConfiguration, match="takes a minimum, a maximum and a step"):
        row(SettingKind.COUNT, minimum=1)


def test_another_kind_states_no_range() -> None:
    with pytest.raises(InvalidConfiguration, match="holds no range"):
        row(SettingKind.TOGGLE, minimum=1, maximum=2, step=1)


def test_a_range_reads_upward() -> None:
    with pytest.raises(InvalidConfiguration, match="runs from 8 down to 1"):
        row(SettingKind.COUNT, minimum=8, maximum=1, step=1)


def test_a_step_moves() -> None:
    with pytest.raises(InvalidConfiguration, match="steps by 0"):
        row(SettingKind.COUNT, minimum=1, maximum=8, step=0)


def test_only_an_optional_setting_lifts_its_limit() -> None:
    with pytest.raises(InvalidConfiguration, match="lifts its limit"):
        row(SettingKind.COUNT, minimum=1, maximum=8, step=1, unlimited=True)


@pytest.mark.parametrize("setting", numbered())
def test_each_range_is_the_one_a_table_is_held_to(setting: SettingName) -> None:
    bounds = bounds_of(setting)
    assert settled(setting, bounds.minimum).rules.model_dump()[setting.value] == bounds.minimum
    assert settled(setting, bounds.maximum).rules.model_dump()[setting.value] == bounds.maximum
    with pytest.raises(SettingOutOfRange, match=setting.value):
        settled(setting, bounds.minimum - 1)

    with pytest.raises(SettingOutOfRange, match=setting.value):
        settled(setting, bounds.maximum + 1)


@pytest.mark.parametrize("setting", numbered())
def test_a_setting_takes_no_value_only_where_the_range_says_so(setting: SettingName) -> None:
    if bounds_of(setting).unlimited:
        assert settled(setting, None).rules.model_dump()[setting.value] is None
        return

    with pytest.raises(ValidationError, match=setting.value):
        settled(setting, None)


def test_a_setting_whose_range_holds_a_limit_takes_a_value() -> None:
    held = _without_the_lifted_limit(SettingName.PER_TURN_SECONDS)
    rules = stated(SettingName.PER_TURN_SECONDS, None)
    with pytest.raises(SettingOutOfRange, match="per_turn_seconds"):
        ensure_within_limits(rules, held)


def test_the_letters_state_the_range_one_letter_number_takes() -> None:
    bounds = bounds_of(SettingName.LETTERS)
    assert bounds.minimum == 0
    adjusted = {"Ź": {"value": bounds.maximum, "count": 1}}
    assert settled(SettingName.LETTERS, adjusted).rules.letters["Ź"].value == bounds.maximum


def test_a_letter_stands_inside_the_range_the_catalog_narrows() -> None:
    narrowed = _narrowed(SettingName.LETTERS, maximum=30)
    rules = stated(SettingName.LETTERS, {"Ź": {"value": 40}})
    with pytest.raises(SettingOutOfRange, match="the letter Ź"):
        ensure_within_limits(rules, narrowed)


def test_every_rung_is_a_value_a_table_may_state() -> None:
    for allowance in catalog().allowances:
        if allowance.offered is None:
            continue

        bounds = bounds_of(allowance.setting)
        for rung in allowance.offered:
            assert bounds.minimum <= rung <= bounds.maximum
            settled_value = settled(allowance.setting, rung).rules.model_dump()
            assert settled_value[allowance.setting.value] == rung


def test_a_choice_the_disk_does_not_hold_names_its_own_values() -> None:
    described = {allowance.setting: allowance for allowance in setting_allowances(CONFIG_DIR)}
    assert described[SettingName.ENDING].choices == ("first_out", "all_out")
    assert described[SettingName.BOARD].choices == ("literaki", "scrabble")


def test_a_row_that_is_no_choice_names_no_values() -> None:
    with pytest.raises(InvalidConfiguration, match="names some"):
        row(SettingKind.TOGGLE, choices=("yes", "no"))


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
            assert scheme.rules.model_dump()[setting.value] in choices[setting]


def _without_the_lifted_limit(setting: SettingName) -> AllowanceCatalog:
    return AllowanceCatalog(
        allowances=tuple(
            (
                allowance.model_copy(update={"unlimited": False})
                if allowance.setting is setting
                else allowance
            )
            for allowance in catalog().allowances
        )
    )


def _narrowed(setting: SettingName, *, maximum: int) -> AllowanceCatalog:
    return AllowanceCatalog(
        allowances=tuple(
            (
                allowance.model_copy(update={"maximum": maximum})
                if allowance.setting is setting
                else allowance
            )
            for allowance in catalog().allowances
        )
    )
