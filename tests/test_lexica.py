import itertools

import pytest

from lexica.compile import compile_lexicon, load_compiled_lexicon
from lexica.dictionaries.sjp import iter_sjp_words
from lexica.distribution import letter_counts
from lexica.models import WordEntry, entry_from_word
from lexica.rules import DictionaryRules, apply_rules
from wordbots.registry import BotRegistry
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


def test_compile_round_trip(tmp_path) -> None:
    destination = tmp_path / "tiny.lexicon"
    compile_lexicon(["kot", "kota", "dom"], destination)
    lexicon = load_compiled_lexicon(destination)
    assert lexicon.judge("kot").allowed
    assert not lexicon.judge("koty").allowed
    assert lexicon.has_prefix("ko")


@pytest.mark.skipif(not SJP_ARCHIVE.is_file(), reason="SJP archive not present")
def test_sjp_loader_sample() -> None:
    words = list(itertools.islice(iter_sjp_words(SJP_ARCHIVE), 25))
    assert words[0] == "AA"
    assert all(word == word.upper() for word in words)


def test_bot_registry() -> None:
    class FakeBot:
        def choose(self, position: Position, seat: int) -> Move:
            raise NotImplementedError

    registry = BotRegistry()
    registry.register("fake", FakeBot())
    assert registry.names() == ("fake",)
    assert registry.get("fake") is not None
