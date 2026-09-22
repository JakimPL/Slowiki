import pytest

from wordcore.errors.exceptions import InvalidConfiguration
from wordtable.sources.discovery import latest_release
from wordtable.sources.releases import DiscoveredRelease

INDEX = "https://sjp.pl/sl/growy/"

PAGE = """<html><body>
<p>Do pobrania - lista słów <a href="/sl/dp.phtml">wg zasad</a> dopuszczalności SJP.PL</p>
<p><b style="font-size: medium;"><a href="sjp-20260901.zip">sjp-20260901.zip</a></b></p>
<a target="_blank" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>
<p><b><a href="/sl/growe/">PRZEGLĄDAJ LISTĘ &gt;</a></b></p>
</body></html>"""


def test_the_linked_archive_resolves_against_the_index() -> None:
    assert latest_release(PAGE, INDEX) == DiscoveredRelease(
        stem="sjp-20260901", url="https://sjp.pl/sl/growy/sjp-20260901.zip"
    )


def test_the_newest_of_several_archives_wins() -> None:
    page = '<a href="sjp-20260820.zip">a</a><a href="sjp-20260901.zip">b</a><a href="sjp-20250101.zip">c</a>'
    assert latest_release(page, INDEX).stem == "sjp-20260901"


def test_an_absolute_link_keeps_its_address() -> None:
    page = '<a href="https://mirror.invalid/sjp/sjp-20261001.zip">archive</a>'
    assert latest_release(page, INDEX) == DiscoveredRelease(
        stem="sjp-20261001", url="https://mirror.invalid/sjp/sjp-20261001.zip"
    )


def test_links_shaped_unlike_an_archive_are_passed_over() -> None:
    page = '<a href="sjp-latest.zip">a</a><a href="sjp-20260901.zip.sig">b</a><a>c</a>'
    with pytest.raises(InvalidConfiguration, match="links no SJP archive"):
        latest_release(page, INDEX)
