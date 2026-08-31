from pathlib import Path
from typing import Final

import pytest
from scripts.strings import CATALOG_DIR, Catalog, locale_names, read_catalog

from lexica.names import DictionaryName
from wordcore.tiles.blank import BLANK_CATEGORY
from wordtable.allowances.group import SettingGroup
from wordtable.allowances.name import SettingName
from wordtable.paths import (
    CONFIG_DIR,
    CONFIGURATION_ALPHABETS_PATH,
    CONFIGURATION_BOARDS_PATH,
    CONFIGURATION_DISTRIBUTIONS_PATH,
)
from wordtable.presets.alphabet import DEFAULT_CATEGORY
from wordtable.presets.load import list_presets, load_alphabet_preset

PRESET_KINDS: Final = (
    CONFIGURATION_BOARDS_PATH,
    CONFIGURATION_ALPHABETS_PATH,
    CONFIGURATION_DISTRIBUTIONS_PATH,
)


def catalogs() -> dict[str, Catalog]:
    return {
        locale: read_catalog(CATALOG_DIR / f"{locale}.yaml") for locale in locale_names(CATALOG_DIR)
    }


def locales() -> tuple[str, ...]:
    return locale_names(CATALOG_DIR)


def categories_on_disk() -> tuple[str, ...]:
    named = {DEFAULT_CATEGORY, BLANK_CATEGORY}
    for name in list_presets(CONFIG_DIR, CONFIGURATION_ALPHABETS_PATH):
        alphabet = load_alphabet_preset(CONFIG_DIR, name)
        named.update(letters.category for letters in alphabet.classes)

    return tuple(sorted(named))


def choices_on_disk() -> tuple[str, ...]:
    named = {name.value for name in DictionaryName}
    for kind in PRESET_KINDS:
        named.update(list_presets(CONFIG_DIR, kind))

    return tuple(sorted(named))


def spoken(locale: str, key: str) -> str:
    said = catalogs()[locale].plain.get(key)
    assert said is not None, f"{locale} leaves {key} unsaid"
    return said


@pytest.mark.parametrize("locale", locales())
def test_every_category_on_disk_has_a_word(locale: str) -> None:
    for category in categories_on_disk():
        assert spoken(locale, f"rules.category.{category}")


@pytest.mark.parametrize("locale", locales())
def test_every_choice_on_disk_has_a_word(locale: str) -> None:
    for choice in choices_on_disk():
        assert spoken(locale, f"rules.choice.{choice}")


@pytest.mark.parametrize("locale", locales())
def test_every_setting_has_a_label(locale: str) -> None:
    for setting in SettingName:
        assert spoken(locale, f"rules.setting.{setting.value}")


@pytest.mark.parametrize("locale", locales())
def test_every_group_has_a_heading(locale: str) -> None:
    for group in SettingGroup:
        assert spoken(locale, f"rules.group.{group.value}")


def test_the_catalogs_name_only_what_is_on_disk() -> None:
    authored = _prefixed(CATALOG_DIR / "en.yaml", "rules.category.")
    assert authored == set(categories_on_disk())
    assert _prefixed(CATALOG_DIR / "en.yaml", "rules.choice.") == set(choices_on_disk())


def _prefixed(path: Path, prefix: str) -> set[str]:
    return {key.removeprefix(prefix) for key in read_catalog(path).plain if key.startswith(prefix)}
