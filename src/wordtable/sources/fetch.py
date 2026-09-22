import functools
import hashlib
import logging
import os
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import Final

from lexica.dictionaries.sjp import SJP_WORD_LIST
from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.paths import POLIMORF_TABLE, archive_path, sjp_release_record
from wordtable.sources.discovery import latest_release
from wordtable.sources.record import ReleaseRecord, write_release_record
from wordtable.sources.releases import POLIMORF_RELEASE, SJP_INDEX, SourceRelease

MIRROR_VARIABLE: Final = "SLOWIKI_SOURCE_MIRROR"

_CHUNK: Final = 1 << 20
_PARTIAL_SUFFIX: Final = ".partial"
_PAGE_ENCODING: Final = "utf-8"

logger = logging.getLogger(__name__)


def pinned_sources() -> tuple[tuple[SourceRelease, Path], ...]:
    return ((POLIMORF_RELEASE, POLIMORF_TABLE),)


def fetch_sources() -> tuple[Path, ...]:
    pinned = tuple(fetch_release(release, destination) for release, destination in pinned_sources())
    return (fetch_latest_sjp(SJP_INDEX), *pinned)


def fetch_latest_sjp(index_url: str) -> Path:
    release = latest_release(_read_page(index_url), index_url)
    destination = archive_path(release.stem)
    if not destination.is_file():
        logger.info("downloading %s from %s", destination.name, release.url)
        destination.parent.mkdir(parents=True, exist_ok=True)
        _download(release.url, destination, _ensure_sjp_archive)

    _ensure_sjp_archive(destination, str(destination))
    record = ReleaseRecord(stem=release.stem, url=release.url, sha256=_file_digest(destination))
    write_release_record(sjp_release_record(), record)
    return destination


def fetch_release(release: SourceRelease, destination: Path) -> Path:
    if destination.is_file():
        _ensure_digest_agrees(release, destination, str(destination))
        return destination

    url = source_url(release)
    logger.info("downloading %s from %s", release.filename, url)
    destination.parent.mkdir(parents=True, exist_ok=True)
    _download(url, destination, functools.partial(_ensure_digest_agrees, release))
    return destination


def source_url(release: SourceRelease) -> str:
    mirror = os.environ.get(MIRROR_VARIABLE, "").strip()
    if not mirror:
        return release.url

    return f"{mirror.rstrip('/')}/{release.filename}"


def _read_page(url: str) -> str:
    try:
        with urllib.request.urlopen(url) as response:
            body: bytes = response.read()
    except urllib.error.URLError as error:
        raise InvalidConfiguration(f"the page {url} failed to load: {error}") from error

    return body.decode(_PAGE_ENCODING)


def _download(url: str, destination: Path, ensure_valid: Callable[[Path, str], None]) -> None:
    partial = destination.with_name(destination.name + _PARTIAL_SUFFIX)
    try:
        _stream(url, partial)
        ensure_valid(partial, url)
    except InvalidConfiguration:
        partial.unlink(missing_ok=True)
        raise

    partial.replace(destination)


def _stream(url: str, partial: Path) -> None:
    try:
        with urllib.request.urlopen(url) as response, partial.open("wb") as handle:
            while chunk := response.read(_CHUNK):
                handle.write(chunk)
    except urllib.error.URLError as error:
        raise InvalidConfiguration(f"the download of {url} failed: {error}") from error


def _ensure_digest_agrees(release: SourceRelease, path: Path, origin: str) -> None:
    digest = _file_digest(path)
    if digest != release.sha256:
        raise InvalidConfiguration(
            f"{origin} carries sha256 {digest} where the pinned {release.filename} carries "
            f"{release.sha256}; delete any stale copy and fetch the source again"
        )


def _ensure_sjp_archive(path: Path, origin: str) -> None:
    _ensure_zip_intact(path, origin)
    _ensure_word_list_present(path, origin)


def _ensure_zip_intact(path: Path, origin: str) -> None:
    if not zipfile.is_zipfile(path):
        raise InvalidConfiguration(f"{origin} carries no zip archive")

    try:
        with zipfile.ZipFile(path) as archive:
            damaged = archive.testzip()
    except zipfile.BadZipFile as error:
        raise InvalidConfiguration(f"{origin} carries a damaged zip archive: {error}") from error

    if damaged is not None:
        raise InvalidConfiguration(f"{origin} carries a damaged member {damaged}")


def _ensure_word_list_present(path: Path, origin: str) -> None:
    with zipfile.ZipFile(path) as archive:
        members = archive.namelist()

    if SJP_WORD_LIST not in members:
        raise InvalidConfiguration(f"{origin} carries no word list {SJP_WORD_LIST}")


def _file_digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()
