from pathlib import Path

import pytest

from lexica.grammar.mapping_version import MAPPING_VERSION
from lexica.lore.override import OverrideRow
from lexica.maintenance.manifest import (
    PIPELINE_VERSION,
    build_digests,
    load_manifest,
    write_manifest,
)
from lexica.maintenance.overrides import parse_overrides
from wordcore.errors.exceptions import InvalidConfiguration

KOT = """overrides:
  - form: kot
    analyses:
      - lemma: kot:Sm1
        tag: subst:sg:nom:m1
"""


def _holds(word: str) -> bool:
    return word == "KOT"


def _written(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "sjp.morph.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_an_override_reads_into_a_row_the_lore_can_answer(tmp_path: Path) -> None:
    overrides = parse_overrides(_written(tmp_path, KOT), _holds)
    assert overrides == {"KOT": (OverrideRow(lemma="KOT:SM1", tag="subst:sg:nom:m1"),)}


def test_an_override_of_a_form_outside_the_dictionary_is_refused(tmp_path: Path) -> None:
    path = _written(tmp_path, "overrides:\n  - form: nieznane\n    analyses: []\n")
    with pytest.raises(InvalidConfiguration, match="absent from the dictionary"):
        parse_overrides(path, _holds)


def test_an_override_named_twice_is_refused(tmp_path: Path) -> None:
    path = _written(tmp_path, KOT + "  - form: kot\n    analyses: []\n")
    with pytest.raises(InvalidConfiguration, match="duplicate override form"):
        parse_overrides(path, _holds)


def test_an_override_carrying_no_analysis_forces_the_residual_answer(tmp_path: Path) -> None:
    path = _written(tmp_path, "overrides:\n  - form: kot\n    analyses: []\n")
    assert parse_overrides(path, _holds) == {"KOT": ()}


def test_a_malformed_overrides_file_is_refused(tmp_path: Path) -> None:
    path = _written(tmp_path, "overrides:\n  - form: kot\n")
    with pytest.raises(InvalidConfiguration, match="malformed overrides file"):
        parse_overrides(path, _holds)


def test_a_manifest_round_trips(tmp_path: Path) -> None:
    archive = tmp_path / "sjp.zip"
    archive.write_bytes(b"abc")
    polimorf = tmp_path / "polimorf.tab.gz"
    polimorf.write_bytes(b"def")
    digests = build_digests(archive, polimorf, "dict", MAPPING_VERSION, PIPELINE_VERSION)
    manifest = tmp_path / "sjp.manifest.json"
    write_manifest(manifest, digests)
    assert load_manifest(manifest) == digests
    assert load_manifest(tmp_path / "missing.json") == {}


def test_a_changed_input_moves_its_digest(tmp_path: Path) -> None:
    archive = tmp_path / "sjp.zip"
    archive.write_bytes(b"abc")
    polimorf = tmp_path / "polimorf.tab.gz"
    polimorf.write_bytes(b"def")
    before = build_digests(archive, polimorf, "dict", MAPPING_VERSION, PIPELINE_VERSION)
    polimorf.write_bytes(b"ghi")
    after = build_digests(archive, polimorf, "dict", MAPPING_VERSION, PIPELINE_VERSION)
    assert before["archive"] == after["archive"]
    assert before["polimorf"] != after["polimorf"]
