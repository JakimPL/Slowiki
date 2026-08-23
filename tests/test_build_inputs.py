from pathlib import Path

import pytest

from lexica.lore.override import OverrideRow
from lexica.names import DictionaryName
from wordcore.lexicon.lexicon import TextLexicon
from wordtable import paths
from wordtable.manifest import inputs_stand_recorded, record_inputs
from wordtable.overrides import load_overrides
from wordtable.releases import SJP_RELEASE

OVERRIDES = """overrides:
  - form: kot
    analyses:
      - lemma: kot:Sm1
        tag: subst:sg:nom:m1
"""


@pytest.fixture(name="dictionaries")
def _dictionaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(paths, "DICTIONARIES_DIR", tmp_path)
    return tmp_path


def _sources(dictionaries: Path) -> Path:
    (dictionaries / f"{SJP_RELEASE.stem}.zip").write_bytes(b"archive")
    polimorf = dictionaries / "polimorf.tab.gz"
    polimorf.write_bytes(b"table")
    return polimorf


def test_an_absent_overrides_file_leaves_the_sources_alone(dictionaries: Path) -> None:
    lexicon = TextLexicon.from_words(["KOT"])
    assert load_overrides(DictionaryName.SJP, lexicon) == {}


def test_an_overrides_file_reads_against_the_dictionary(dictionaries: Path) -> None:
    paths.dictionary_overrides(DictionaryName.SJP).write_text(OVERRIDES, encoding="utf-8")
    lexicon = TextLexicon.from_words(["KOT"])
    assert load_overrides(DictionaryName.SJP, lexicon) == {
        "KOT": (OverrideRow(lemma="KOT:SM1", tag="subst:sg:nom:m1"),)
    }


def test_the_recorded_inputs_answer_current_until_a_source_moves(dictionaries: Path) -> None:
    polimorf = _sources(dictionaries)
    record_inputs(DictionaryName.SJP, polimorf)
    assert inputs_stand_recorded(DictionaryName.SJP, polimorf) is True

    polimorf.write_bytes(b"a newer table")
    assert inputs_stand_recorded(DictionaryName.SJP, polimorf) is False

    record_inputs(DictionaryName.SJP, polimorf)
    assert inputs_stand_recorded(DictionaryName.SJP, polimorf) is True


def test_an_artifact_with_no_manifest_stands_stale(dictionaries: Path) -> None:
    polimorf = _sources(dictionaries)
    assert inputs_stand_recorded(DictionaryName.SJP, polimorf) is False


def test_sources_off_disk_leave_the_standing_artifact_alone(dictionaries: Path) -> None:
    polimorf = _sources(dictionaries)
    record_inputs(DictionaryName.SJP, polimorf)
    polimorf.unlink()
    assert inputs_stand_recorded(DictionaryName.SJP, polimorf) is True
