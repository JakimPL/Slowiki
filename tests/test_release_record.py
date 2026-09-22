from pathlib import Path

import pytest

from lexica.artifact.kind import ArtifactKind
from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordtable import paths
from wordtable.lexicons import dictionary_ready
from wordtable.sources.record import ReleaseRecord, read_release_record, write_release_record

RECORD = ReleaseRecord(
    stem="sjp-20260101", url="https://example.invalid/sjp-20260101.zip", sha256="0" * 64
)


@pytest.fixture(name="dictionaries")
def _dictionaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(paths, "DICTIONARIES_DIR", tmp_path)
    return tmp_path


def test_a_record_reads_back_as_written(tmp_path: Path) -> None:
    record = tmp_path / "nested" / "sjp.release.json"
    write_release_record(record, RECORD)
    assert read_release_record(record) == RECORD


def test_an_absent_record_reads_as_none(tmp_path: Path) -> None:
    assert read_release_record(tmp_path / "sjp.release.json") is None


def test_the_record_names_every_sjp_path(dictionaries: Path) -> None:
    write_release_record(paths.sjp_release_record(), RECORD)
    assert paths.dictionary_known(DictionaryName.SJP) is True
    assert paths.dictionary_archive(DictionaryName.SJP) == dictionaries / "sjp-20260101.zip"
    assert paths.dictionary_compiled(DictionaryName.SJP, ArtifactKind.WORDS) == (
        dictionaries / "sjp-20260101.words.v1.lexicon"
    )


def test_an_unrecorded_sjp_release_leaves_the_dictionary_unready(dictionaries: Path) -> None:
    assert paths.dictionary_known(DictionaryName.SJP) is False
    assert dictionary_ready(DictionaryName.SJP) is False
    with pytest.raises(InvalidConfiguration, match="run 'wordtable fetch'"):
        paths.dictionary_archive(DictionaryName.SJP)


def test_named_dictionaries_stand_known_without_a_record(dictionaries: Path) -> None:
    assert paths.dictionary_known(DictionaryName.OSPS) is True
    assert paths.dictionary_known(DictionaryName.ENGLISH) is True
