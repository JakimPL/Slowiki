import marshal
from pathlib import Path

import pytest

from lexica.artifact.envelope import MAGIC, read_header, write_envelope
from lexica.artifact.formats import ARTIFACT_FORMATS
from lexica.artifact.header import ArtifactHeader
from lexica.artifact.kind import ArtifactKind
from lexica.artifact.words import read_word_list, write_word_list
from lexica.cli import main
from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.paths import dictionary_compiled

WORDS = ("DOM", "KOT", "KOTA")


def _artifact(tmp_path: Path) -> Path:
    destination = tmp_path / "tiny.words.v1.lexicon"
    write_word_list(["kot", "kota", "dom"], destination)
    return destination


def test_every_kind_declares_a_current_format() -> None:
    assert set(ARTIFACT_FORMATS) == set(ArtifactKind)


def test_compiled_names_carry_the_kind() -> None:
    words = dictionary_compiled(DictionaryName.SJP, ArtifactKind.WORDS)
    lore = dictionary_compiled(DictionaryName.SJP, ArtifactKind.LORE)
    assert words.name == "sjp-20260803.words.v1.lexicon"
    assert lore.name == "sjp-20260803.lore.v1.lexicon"


def test_word_list_round_trip(tmp_path: Path) -> None:
    lexicon = read_word_list(_artifact(tmp_path))
    assert lexicon.words == WORDS
    assert lexicon.judge("kot").allowed
    assert not lexicon.judge("koty").allowed
    assert lexicon.has_prefix("ko")


def test_the_header_reads_without_the_body(tmp_path: Path) -> None:
    header = read_header(_artifact(tmp_path))
    assert header == ArtifactHeader(kind=ArtifactKind.WORDS, format=1, entries=3)


def test_writing_leaves_no_partial_file(tmp_path: Path) -> None:
    _artifact(tmp_path)
    assert [path.name for path in tmp_path.iterdir()] == ["tiny.words.v1.lexicon"]


def test_a_lore_artifact_is_refused_where_a_word_list_belongs(tmp_path: Path) -> None:
    destination = tmp_path / "tiny.words.v1.lexicon"
    header = ArtifactHeader(kind=ArtifactKind.LORE, format=1, entries=0)
    write_envelope(destination, header, b"")
    with pytest.raises(InvalidConfiguration, match="holds a lore artifact where a words artifact"):
        read_word_list(destination)


def test_a_headerless_file_is_refused(tmp_path: Path) -> None:
    destination = tmp_path / "legacy.lexicon"
    destination.write_bytes(marshal.dumps(WORDS))
    with pytest.raises(InvalidConfiguration, match="carries no artifact header"):
        read_word_list(destination)


def test_a_file_ending_inside_its_header_is_refused(tmp_path: Path) -> None:
    destination = tmp_path / "short.lexicon"
    destination.write_bytes(MAGIC + b"\x00")
    with pytest.raises(InvalidConfiguration, match="ends inside its artifact header"):
        read_header(destination)


def test_an_unreadable_header_is_refused(tmp_path: Path) -> None:
    destination = tmp_path / "garbled.lexicon"
    destination.write_bytes(MAGIC + (4).to_bytes(4, "big") + b"{ , }")
    with pytest.raises(InvalidConfiguration, match="unreadable artifact header"):
        read_header(destination)


def test_a_retired_format_is_refused(tmp_path: Path) -> None:
    destination = tmp_path / "stale.lexicon"
    header = ArtifactHeader(kind=ArtifactKind.WORDS, format=0, entries=0)
    write_envelope(destination, header, marshal.dumps(()))
    with pytest.raises(InvalidConfiguration, match="format 0 where format 1 belongs"):
        read_word_list(destination)


def test_a_damaged_body_is_refused(tmp_path: Path) -> None:
    destination = _artifact(tmp_path)
    destination.write_bytes(destination.read_bytes()[:-3])
    with pytest.raises(InvalidConfiguration, match="damaged word list"):
        read_word_list(destination)


def test_a_body_of_the_wrong_shape_is_refused(tmp_path: Path) -> None:
    destination = tmp_path / "shaped.lexicon"
    header = ArtifactHeader(kind=ArtifactKind.WORDS, format=1, entries=1)
    write_envelope(destination, header, marshal.dumps({"KOT": 1}))
    with pytest.raises(InvalidConfiguration, match="word list of an unreadable shape"):
        read_word_list(destination)


def test_a_miscounted_word_list_is_refused(tmp_path: Path) -> None:
    destination = tmp_path / "miscounted.lexicon"
    header = ArtifactHeader(kind=ArtifactKind.WORDS, format=1, entries=5)
    write_envelope(destination, header, marshal.dumps(WORDS))
    with pytest.raises(InvalidConfiguration, match="declares 5 words and holds 3"):
        read_word_list(destination)


def test_the_header_command_reports_the_kind(tmp_path: Path, capsys) -> None:
    destination = _artifact(tmp_path)
    main(["header", str(destination)])
    assert "words format 1, 3 entries" in capsys.readouterr().out
