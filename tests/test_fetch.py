import hashlib
from pathlib import Path

import pytest

from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.fetch import MIRROR_VARIABLE, fetch_release, pinned_sources, source_url
from wordtable.releases import POLIMORF_RELEASE, SJP_RELEASE, SourceRelease

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
    assert releases == {SJP_RELEASE, POLIMORF_RELEASE}
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
