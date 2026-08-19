from pathlib import Path

import pytest
from scripts.contract import DOCUMENT, MANIFEST, contract_names, kind_rows, main

from wordcore.errors.exceptions import InvalidConfiguration

CONTRACT = """# The lexicon contract

## Kinds

| Kind | Format | File name | Producer | Reader | Consumer |
| --- | --- | --- | --- | --- | --- |
| `words` | 1 | `{stem}.words.v1.lexicon` | `lexica.artifact.words.write_word_list` \
| `lexica.artifact.words.read_word_list` | `wordtable.lexicons.load_lexicon` |
| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — | — |

## Envelope

| Constant | Value |
| --- | --- |
| `lexica.artifact.envelope.MAGIC` | `LITERABBLE` |

## Boundaries

| Boundary | Enforced by |
| --- | --- |
| `lexica` imports no host | `Pure layers know no adapter or host` |
"""


def written(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "lexicon-contract.md"
    path.write_text(body, encoding="utf-8")
    return path


def refused(tmp_path: Path, original: str, replacement: str) -> Path:
    assert original in CONTRACT
    return written(tmp_path, CONTRACT.replace(original, replacement))


def test_the_contract_agrees_with_the_code() -> None:
    main(DOCUMENT, MANIFEST)


def test_the_import_contracts_are_declared() -> None:
    assert "Core knows no subsystem" in contract_names(MANIFEST)


def test_a_reserved_kind_needs_no_code(tmp_path: Path) -> None:
    rows = kind_rows(written(tmp_path, CONTRACT))
    assert rows[1].kind == "lore"
    assert rows[1].producer == "—"
    main(written(tmp_path, CONTRACT), MANIFEST)


def test_a_stale_format_is_refused(tmp_path: Path) -> None:
    document = refused(tmp_path, "| `lore` | 1 |", "| `lore` | 2 |")
    with pytest.raises(InvalidConfiguration, match="declares format 2"):
        main(document, MANIFEST)


def test_an_unnumbered_format_is_refused(tmp_path: Path) -> None:
    document = refused(tmp_path, "| `lore` | 1 |", "| `lore` | first |")
    with pytest.raises(InvalidConfiguration, match="names no format"):
        main(document, MANIFEST)


def test_a_kind_without_a_row_is_refused(tmp_path: Path) -> None:
    document = refused(tmp_path, "| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — | — |\n", "")
    with pytest.raises(InvalidConfiguration, match="the artifact kind lore carries no row"):
        main(document, MANIFEST)


def test_a_row_naming_no_kind_is_refused(tmp_path: Path) -> None:
    document = refused(
        tmp_path,
        "| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — | — |",
        "| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — | — |\n"
        "| `runes` | 1 | `{stem}.runes.v1.lexicon` | — | — | — |",
    )
    with pytest.raises(InvalidConfiguration, match="the row runes names no artifact kind"):
        main(document, MANIFEST)


def test_a_repeated_kind_is_refused(tmp_path: Path) -> None:
    document = refused(
        tmp_path,
        "| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — | — |",
        "| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — | — |\n"
        "| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — | — |",
    )
    with pytest.raises(InvalidConfiguration, match="the kind lore carries more than one row"):
        main(document, MANIFEST)


def test_a_drifted_file_name_is_refused(tmp_path: Path) -> None:
    document = refused(tmp_path, "`{stem}.lore.v1.lexicon`", "`{stem}.v1.lexicon`")
    with pytest.raises(InvalidConfiguration, match="where the contract declares"):
        main(document, MANIFEST)


def test_a_renamed_reader_is_refused(tmp_path: Path) -> None:
    document = refused(tmp_path, "words.read_word_list", "words.read_words")
    with pytest.raises(InvalidConfiguration, match="the words reader .* is absent from the code"):
        main(document, MANIFEST)


def test_a_reader_in_a_missing_module_is_refused(tmp_path: Path) -> None:
    document = refused(tmp_path, "lexica.artifact.words.read_word_list", "lexica.reader.words")
    with pytest.raises(InvalidConfiguration, match="names the missing module lexica.reader"):
        main(document, MANIFEST)


def test_a_changed_envelope_constant_is_refused(tmp_path: Path) -> None:
    document = refused(tmp_path, "| `LITERABBLE` |", "| `LITERAKI` |")
    with pytest.raises(InvalidConfiguration, match="holds LITERABBLE where the contract declares"):
        main(document, MANIFEST)


def test_an_undeclared_import_contract_is_refused(tmp_path: Path) -> None:
    document = refused(tmp_path, "`Pure layers know no adapter or host`", "`Layers stay pure`")
    with pytest.raises(InvalidConfiguration, match="names the import contract Layers stay pure"):
        main(document, MANIFEST)


def test_a_missing_section_is_refused(tmp_path: Path) -> None:
    document = refused(tmp_path, "## Envelope", "### Envelope")
    with pytest.raises(InvalidConfiguration, match="the section Envelope is missing"):
        main(document, MANIFEST)


def test_a_section_without_a_table_is_refused(tmp_path: Path) -> None:
    document = refused(
        tmp_path,
        "| `lexica.artifact.envelope.MAGIC` | `LITERABBLE` |",
        "the constants land here",
    )
    with pytest.raises(InvalidConfiguration, match="the section Envelope carries no table"):
        main(document, MANIFEST)


def test_a_row_of_the_wrong_width_is_refused(tmp_path: Path) -> None:
    document = refused(
        tmp_path,
        "| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — | — |",
        "| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — |",
    )
    with pytest.raises(InvalidConfiguration, match="carries 5 columns where 6 belong"):
        main(document, MANIFEST)
