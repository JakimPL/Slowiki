from pathlib import Path

import pytest

from lexica.grammar.mapping_version import MAPPING_VERSION
from lexica.maintenance.manifest import (
    PIPELINE_VERSION,
    compile_input_digests,
    load_manifest,
    write_manifest,
)
from lexica.maintenance.overrides import parse_overrides
from wordcore.errors.exceptions import InvalidConfiguration


def test_parse_overrides_validates_forms(tmp_path: Path) -> None:
    path = tmp_path / "overrides.morph.yaml"
    path.write_text(
        "overrides:\n"
        "  - form: kot\n"
        "    analyses:\n"
        "      - lemma: kot:Sm1\n"
        "        tag: subst:sg:nom:m1\n",
        encoding="utf-8",
    )
    overrides = parse_overrides(path, frozenset({"KOT"}))
    assert overrides == {"KOT": (("KOT:SM1", "subst:sg:nom:m1"),)}

    path.write_text(
        "overrides:\n  - form: nieznane\n    analyses: []\n",
        encoding="utf-8",
    )
    with pytest.raises(InvalidConfiguration):
        parse_overrides(path, frozenset({"KOT"}))


def test_manifest_round_trip(tmp_path: Path) -> None:
    archive = tmp_path / "sjp.zip"
    archive.write_bytes(b"abc")
    digests = compile_input_digests(archive, None, None, "dict", MAPPING_VERSION, PIPELINE_VERSION)
    manifest = tmp_path / "manifest.json"
    write_manifest(manifest, digests)
    assert load_manifest(manifest) == digests
    assert load_manifest(tmp_path / "missing.json") == {}
