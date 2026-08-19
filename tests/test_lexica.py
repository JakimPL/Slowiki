import itertools
import zipfile

import pytest

from lexica.dictionaries.catalog import iter_dictionary_words
from lexica.dictionaries.plain import iter_plain_words
from lexica.dictionaries.sjp import iter_sjp_words
from lexica.distribution import letter_counts
from lexica.models import WordEntry, entry_from_word
from lexica.names import DictionaryName
from lexica.rules import DictionaryRules, apply_rules
from wordbots.registry import BotRegistry
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.moves.move import Move
from wordcore.positions.position import Position
from wordtable.paths import PROJECT_ROOT

SJP_ARCHIVE = PROJECT_ROOT / "dictionaries" / "sjp-20260803.zip"


def test_word_entry_model() -> None:
    entry = WordEntry(surface="zamek", homonym_id=1, categories=frozenset({"noun"}))
    assert entry.surface == "zamek"
    assert entry.homonym_id == 1


def test_entry_from_word() -> None:
    entry = entry_from_word("kot", source="sjp")
    assert entry.source == "sjp"
    assert entry.categories == frozenset()


def test_apply_rules_bounds_and_patterns() -> None:
    rules = DictionaryRules(min_length=2, max_length=4, excluded_patterns=("-",))
    words = ("a", "ab", "abcd", "abcde", "a-b")
    assert apply_rules(words, rules) == ("ab", "abcd")


def test_letter_counts() -> None:
    assert letter_counts(["aa", "ab"]) == {"A": 3, "B": 1}


@pytest.mark.skipif(not SJP_ARCHIVE.is_file(), reason="SJP archive not present")
def test_sjp_loader_sample() -> None:
    words = list(itertools.islice(iter_sjp_words(SJP_ARCHIVE), 25))
    assert words[0] == "AA"
    assert all(word == word.upper() for word in words)


def test_plain_loader_reads_every_word_list(tmp_path) -> None:
    archive = tmp_path / "english.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("b-words.txt", "bat\nbee\n")
        bundle.writestr("a-words.txt", "ant\n\nape\n")
        bundle.writestr("README.txt", "license text")
    assert list(iter_plain_words(archive)) == ["ANT", "APE", "BAT", "BEE"]


def test_plain_loader_rejects_an_empty_bundle(tmp_path) -> None:
    archive = tmp_path / "empty.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("README.txt", "license text")
    with pytest.raises(InvalidConfiguration):
        list(iter_plain_words(archive))


def test_dictionary_catalog_maps_every_source(tmp_path) -> None:
    archive = tmp_path / "osps.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("words.txt", "dom\n")
    assert list(iter_dictionary_words(DictionaryName.OSPS, archive)) == ["DOM"]


def test_bot_registry() -> None:
    class FakeBot:
        def choose(self, position: Position, seat: int) -> Move:
            raise NotImplementedError

    registry = BotRegistry()
    registry.register("fake", FakeBot())
    assert registry.names() == ("fake",)
    assert registry.get("fake") is not None
