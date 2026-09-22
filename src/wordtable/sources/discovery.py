import re
from html.parser import HTMLParser
from pathlib import PurePosixPath
from typing import Final, NamedTuple
from urllib.parse import urljoin, urlparse

from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.sources.releases import DiscoveredRelease

SJP_ARCHIVE_PATTERN: Final = re.compile(r"(?P<stem>sjp-\d{8})\.zip")


class _ArchiveLink(NamedTuple):
    stem: str
    href: str


class _LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        self.links.extend(value for name, value in attrs if name == "href" and value is not None)


def latest_release(page: str, index_url: str) -> DiscoveredRelease:
    archives = _archive_links(_links_of(page))
    _ensure_archive_linked(archives, index_url)
    newest = max(archives, key=lambda archive: archive.stem)
    return DiscoveredRelease(stem=newest.stem, url=urljoin(index_url, newest.href))


def _links_of(page: str) -> tuple[str, ...]:
    collector = _LinkCollector()
    collector.feed(page)
    collector.close()
    return tuple(collector.links)


def _archive_links(links: tuple[str, ...]) -> tuple[_ArchiveLink, ...]:
    archives: list[_ArchiveLink] = []
    for href in links:
        match = SJP_ARCHIVE_PATTERN.fullmatch(PurePosixPath(urlparse(href).path).name)
        if match is not None:
            archives.append(_ArchiveLink(stem=match["stem"], href=href))

    return tuple(archives)


def _ensure_archive_linked(archives: tuple[_ArchiveLink, ...], index_url: str) -> None:
    if not archives:
        raise InvalidConfiguration(f"{index_url} links no SJP archive")
