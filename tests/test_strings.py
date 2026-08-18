from pathlib import Path

import pytest
from scripts.strings import (
    CATALOG_DIR,
    OUTPUT_DIR,
    Placeholder,
    locale_names,
    main,
    read_catalog,
    resolved_catalog,
    shape_of,
)

from wordcore.errors.exceptions import InvalidConfiguration

REFERENCE = """
arrive:
  code_label: Table code
  offering:
    plural:
      one: "{name} · {span} player"
      other: "{name} · {span} players"
seats:
  gathering: "{present:number} of {total:number}"
"""


def written(directory: Path, locale: str, body: str) -> Path:
    path = directory / f"{locale}.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def resolved(tmp_path: Path, locale: str, body: str) -> None:
    reference = read_catalog(written(tmp_path, "en", REFERENCE))
    authored = read_catalog(written(tmp_path, locale, body))
    resolved_catalog(locale, authored, shape_of(reference))


def test_reads_nested_namespaces_as_dotted_keys(tmp_path: Path) -> None:
    catalog = read_catalog(written(tmp_path, "en", REFERENCE))
    assert sorted(catalog.plain) == ["arrive.code_label", "seats.gathering"]
    assert sorted(catalog.plural) == ["arrive.offering"]
    assert sorted(catalog.plural["arrive.offering"]) == ["one", "other"]


def test_shape_carries_the_declared_placeholders(tmp_path: Path) -> None:
    shape = shape_of(read_catalog(written(tmp_path, "en", REFERENCE)))
    assert shape.plain["seats.gathering"] == (
        Placeholder(name="present", numeric=True),
        Placeholder(name="total", numeric=True),
    )
    assert shape.plain["arrive.code_label"] == ()
    assert shape.plural["arrive.offering"] == (
        Placeholder(name="name", numeric=False),
        Placeholder(name="span", numeric=False),
    )


def test_emitted_templates_drop_the_type_declarations(tmp_path: Path) -> None:
    reference = read_catalog(written(tmp_path, "en", REFERENCE))
    catalog = resolved_catalog("en", reference, shape_of(reference))
    assert catalog.plain["seats.gathering"] == "{present} of {total}"


def test_english_plural_fills_every_category(tmp_path: Path) -> None:
    reference = read_catalog(written(tmp_path, "en", REFERENCE))
    catalog = resolved_catalog("en", reference, shape_of(reference))
    entry = catalog.plural["arrive.offering"]
    assert entry["one"] == "{name} · {span} player"
    assert entry["few"] == entry["many"] == entry["other"] == "{name} · {span} players"


def test_locale_names_lead_with_the_reference(tmp_path: Path) -> None:
    written(tmp_path, "en", REFERENCE)
    written(tmp_path, "pl", REFERENCE)
    assert locale_names(tmp_path) == ("en", "pl")


def test_refuses_a_directory_without_the_reference(tmp_path: Path) -> None:
    written(tmp_path, "pl", REFERENCE)
    with pytest.raises(InvalidConfiguration, match="reference catalog"):
        locale_names(tmp_path)


def test_refuses_a_locale_with_undeclared_plural_categories(tmp_path: Path) -> None:
    with pytest.raises(InvalidConfiguration, match="plural categories are undeclared"):
        resolved(tmp_path, "kl", REFERENCE)


def test_refuses_a_missing_message(tmp_path: Path) -> None:
    body = REFERENCE.replace("  code_label: Table code\n", "")
    with pytest.raises(InvalidConfiguration, match="arrive.code_label is missing"):
        resolved(tmp_path, "pl", body)


def test_refuses_a_message_the_reference_lacks(tmp_path: Path) -> None:
    body = REFERENCE + "words:\n  label: Formed words\n"
    with pytest.raises(InvalidConfiguration, match="absent from the reference"):
        resolved(tmp_path, "pl", body)


def test_refuses_a_missing_plural_message(tmp_path: Path) -> None:
    body = "arrive:\n  code_label: Table code\nseats:\n  gathering: '{present:number} of {total:number}'\n"
    with pytest.raises(InvalidConfiguration, match="plural message arrive.offering is missing"):
        resolved(tmp_path, "pl", body)


def test_refuses_mismatched_placeholders(tmp_path: Path) -> None:
    body = REFERENCE.replace("{present:number} of {total:number}", "{present:number} at the table")
    with pytest.raises(InvalidConfiguration, match="seats.gathering carries present"):
        resolved(tmp_path, "pl", body)


def test_refuses_an_empty_message(tmp_path: Path) -> None:
    body = REFERENCE.replace("code_label: Table code", 'code_label: " "')
    with pytest.raises(InvalidConfiguration, match="carries no message"):
        resolved(tmp_path, "pl", body)


def test_refuses_incomplete_plural_categories(tmp_path: Path) -> None:
    body = REFERENCE.replace('      other: "{name} · {span} players"\n', "")
    with pytest.raises(InvalidConfiguration, match="needs the categories"):
        resolved(tmp_path, "pl", body)


def test_refuses_categories_that_disagree_on_placeholders(tmp_path: Path) -> None:
    body = REFERENCE.replace('other: "{name} · {span} players"', 'other: "{name} players"')
    with pytest.raises(InvalidConfiguration, match="different placeholders"):
        shape_of(read_catalog(written(tmp_path, "en", body)))


def test_refuses_a_placeholder_that_is_not_a_name(tmp_path: Path) -> None:
    body = REFERENCE.replace("{present:number}", "{Present}")
    with pytest.raises(InvalidConfiguration, match="not a placeholder"):
        shape_of(read_catalog(written(tmp_path, "en", body)))


def test_refuses_unbalanced_braces(tmp_path: Path) -> None:
    body = REFERENCE.replace(
        "{present:number} of {total:number}", "{present:number of {total:number}"
    )
    with pytest.raises(InvalidConfiguration, match="braces are unbalanced"):
        shape_of(read_catalog(written(tmp_path, "en", body)))


def test_refuses_the_reserved_count_in_a_plain_message(tmp_path: Path) -> None:
    body = REFERENCE.replace("{present:number} of {total:number}", "{count:number} at the table")
    with pytest.raises(InvalidConfiguration, match="count belongs to plural messages"):
        shape_of(read_catalog(written(tmp_path, "en", body)))


def test_refuses_a_count_that_is_not_a_number(tmp_path: Path) -> None:
    body = REFERENCE.replace("{name} · {span} player", "{count} · {name} {span} player").replace(
        "{name} · {span} players", "{count} · {name} {span} players"
    )
    with pytest.raises(InvalidConfiguration, match="count must be declared as a number"):
        shape_of(read_catalog(written(tmp_path, "en", body)))


def test_refuses_a_plural_message_holding_more_than_categories(tmp_path: Path) -> None:
    body = REFERENCE.replace(
        "  offering:\n    plural:\n", "  offering:\n    note: aside\n    plural:\n"
    )
    with pytest.raises(InvalidConfiguration, match="nothing beside its categories"):
        read_catalog(written(tmp_path, "en", body))


def test_refuses_a_leaf_that_is_neither_message_nor_namespace(tmp_path: Path) -> None:
    body = REFERENCE.replace("code_label: Table code", "code_label: 12")
    with pytest.raises(InvalidConfiguration, match="expected a message or a namespace"):
        read_catalog(written(tmp_path, "en", body))


def test_generation_reproduces_the_committed_sources(tmp_path: Path) -> None:
    main(CATALOG_DIR, tmp_path)
    expected = {"keys.ts", *(f"{locale}.ts" for locale in locale_names(CATALOG_DIR))}
    assert {path.name for path in tmp_path.iterdir()} == expected
    for name in sorted(expected):
        assert (tmp_path / name).read_text(encoding="utf-8") == (OUTPUT_DIR / name).read_text(
            encoding="utf-8"
        )
