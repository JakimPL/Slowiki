import hashlib
import zipfile
from pathlib import Path

import pytest

from wordcore.errors.exceptions import InvalidConfiguration
from wordtable import paths
from wordtable.sources.fetch import (
    MIRROR_VARIABLE,
    fetch_latest_sjp,
    fetch_release,
    pinned_sources,
    source_url,
)
from wordtable.sources.record import ReleaseRecord, read_release_record
from wordtable.sources.releases import POLIMORF_RELEASE, SourceRelease

BODY = b"a pinned source\n"

RELEASE = SourceRelease(
    stem="tiny-20260101",
    suffix=".zip",
    origin="https://example.invalid/lists/",
    sha256=hashlib.sha256(BODY).hexdigest(),
)


def test_a_release_names_its_file_and_its_origin() -> None:
    assert RELEASE.filename == "tiny-20260101.zip"
    assert RELEASE.url == "https://example.invalid/lists/tiny-20260101.zip"


def test_an_unset_mirror_leaves_the_upstream_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(MIRROR_VARIABLE, raising=False)
    assert source_url(RELEASE) == RELEASE.url


def test_a_mirror_keeps_the_pinned_file_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(MIRROR_VARIABLE, "https://mirror.invalid/slowiki/")
    assert source_url(RELEASE) == "https://mirror.invalid/slowiki/tiny-20260101.zip"


def test_a_blank_mirror_leaves_the_upstream_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(MIRROR_VARIABLE, "  ")
    assert source_url(RELEASE) == RELEASE.url


def test_a_present_source_of_the_pinned_digest_is_kept(tmp_path: Path) -> None:
    destination = tmp_path / RELEASE.filename
    destination.write_bytes(BODY)
    assert fetch_release(RELEASE, destination) == destination


def test_a_present_source_of_another_digest_is_refused(tmp_path: Path) -> None:
    destination = tmp_path / RELEASE.filename
    destination.write_bytes(b"another list\n")
    with pytest.raises(InvalidConfiguration, match="carries sha256"):
        fetch_release(RELEASE, destination)


def test_every_pinned_source_lands_beside_the_dictionaries() -> None:
    releases = {release for release, _ in pinned_sources()}
    assert releases == {POLIMORF_RELEASE}
    for release, destination in pinned_sources():
        assert destination.name == release.filename


def test_a_download_of_another_digest_leaves_no_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    served = tmp_path / "mirror" / RELEASE.filename
    served.parent.mkdir()
    served.write_bytes(b"another list\n")
    monkeypatch.setenv(MIRROR_VARIABLE, served.parent.as_uri())
    destination = tmp_path / RELEASE.filename
    with pytest.raises(InvalidConfiguration, match="carries sha256"):
        fetch_release(RELEASE, destination)

    assert not destination.exists()
    assert not destination.with_name(destination.name + ".partial").exists()


@pytest.fixture(name="dictionaries")
def _dictionaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    dictionaries = tmp_path / "dictionaries"
    monkeypatch.setattr(paths, "DICTIONARIES_DIR", dictionaries)
    return dictionaries


def _served_index(tmp_path: Path, archive_name: str) -> str:
    served = tmp_path / "served"
    served.mkdir()
    index = served / "index.html"
    index.write_text(f'<p><b><a href="{archive_name}">{archive_name}</a></b></p>', encoding="utf-8")
    return index.as_uri()


def _sjp_archive(path: Path) -> bytes:
    with zipfile.ZipFile(path, "w") as bundle:
        bundle.writestr("slowa.txt", "aa\r\nab\r\n")
        bundle.writestr("README.txt", "license\n")

    return path.read_bytes()


def test_the_linked_archive_downloads_and_is_recorded(tmp_path: Path, dictionaries: Path) -> None:
    index = _served_index(tmp_path, "sjp-20261001.zip")
    body = _sjp_archive(tmp_path / "served" / "sjp-20261001.zip")
    fetched = fetch_latest_sjp(index)
    assert fetched == dictionaries / "sjp-20261001.zip"
    assert fetched.read_bytes() == body
    assert read_release_record(paths.sjp_release_record()) == ReleaseRecord(
        stem="sjp-20261001",
        url=(tmp_path / "served" / "sjp-20261001.zip").as_uri(),
        sha256=hashlib.sha256(body).hexdigest(),
    )


def test_an_archive_on_disk_is_kept_and_recorded(tmp_path: Path, dictionaries: Path) -> None:
    index = _served_index(tmp_path, "sjp-20261001.zip")
    dictionaries.mkdir()
    body = _sjp_archive(dictionaries / "sjp-20261001.zip")
    assert fetch_latest_sjp(index).read_bytes() == body
    record = read_release_record(paths.sjp_release_record())
    assert record is not None
    assert record.sha256 == hashlib.sha256(body).hexdigest()


def test_a_damaged_archive_leaves_no_file_and_no_record(tmp_path: Path, dictionaries: Path) -> None:
    index = _served_index(tmp_path, "sjp-20261001.zip")
    (tmp_path / "served" / "sjp-20261001.zip").write_bytes(b"an html error page")
    with pytest.raises(InvalidConfiguration, match="carries no zip archive"):
        fetch_latest_sjp(index)

    assert not (dictionaries / "sjp-20261001.zip").exists()
    assert not (dictionaries / "sjp-20261001.zip.partial").exists()
    assert not paths.sjp_release_record().exists()


def test_an_archive_without_the_word_list_is_refused(tmp_path: Path, dictionaries: Path) -> None:
    index = _served_index(tmp_path, "sjp-20261001.zip")
    with zipfile.ZipFile(tmp_path / "served" / "sjp-20261001.zip", "w") as bundle:
        bundle.writestr("README.txt", "license\n")

    with pytest.raises(InvalidConfiguration, match="carries no word list"):
        fetch_latest_sjp(index)

    assert not paths.sjp_release_record().exists()


def test_an_unreachable_index_is_reported(tmp_path: Path, dictionaries: Path) -> None:
    with pytest.raises(InvalidConfiguration, match="failed to load"):
        fetch_latest_sjp((tmp_path / "absent.html").as_uri())
