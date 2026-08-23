import hashlib
import logging
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Final

from lexica.names import DictionaryName
from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.paths import POLIMORF_TABLE, dictionary_archive
from wordtable.releases import POLIMORF_RELEASE, SJP_RELEASE, SourceRelease

MIRROR_VARIABLE: Final = "SLOWIKI_SOURCE_MIRROR"

_CHUNK: Final = 1 << 20
_PARTIAL_SUFFIX: Final = ".partial"

logger = logging.getLogger(__name__)


def pinned_sources() -> tuple[tuple[SourceRelease, Path], ...]:
    return (
        (SJP_RELEASE, dictionary_archive(DictionaryName.SJP)),
        (POLIMORF_RELEASE, POLIMORF_TABLE),
    )


def fetch_sources() -> tuple[Path, ...]:
    return tuple(fetch_release(release, destination) for release, destination in pinned_sources())


def fetch_release(release: SourceRelease, destination: Path) -> Path:
    if destination.is_file():
        _ensure_digest_agrees(release, destination, str(destination))
        return destination

    url = source_url(release)
    logger.info("downloading %s from %s", release.filename, url)
    destination.parent.mkdir(parents=True, exist_ok=True)
    _download(release, url, destination)
    return destination


def source_url(release: SourceRelease) -> str:
    mirror = os.environ.get(MIRROR_VARIABLE, "").strip()
    if not mirror:
        return release.url

    return f"{mirror.rstrip('/')}/{release.filename}"


def _download(release: SourceRelease, url: str, destination: Path) -> None:
    partial = destination.with_name(destination.name + _PARTIAL_SUFFIX)
    try:
        _stream(url, partial)
        _ensure_digest_agrees(release, partial, url)
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


def _file_digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()
