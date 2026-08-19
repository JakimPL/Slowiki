import pytest

from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.lore.lexeme_id import (
    LexemeId,
    lexeme_id_from_lemma,
    lexeme_id_from_token,
    token_of,
)
from wordcore.errors.exceptions import InvalidConfiguration

LEMMA_CASES = [
    ("kot:Sm1", PartOfSpeech.RZECZOWNIK, "KOT", "Sm1"),
    ("zamek:Sm3~u", PartOfSpeech.RZECZOWNIK, "ZAMEK", "Sm3~u"),
    ("by:M", PartOfSpeech.SPÓJNIK, "BY", "M"),
    ("abbozzo", PartOfSpeech.RZECZOWNIK, "ABBOZZO", ""),
    ("źdźbło:Sn~a", PartOfSpeech.RZECZOWNIK, "ŹDŹBŁO", "Sn~a"),
]


@pytest.mark.parametrize(("lemma", "part", "written", "pattern"), LEMMA_CASES)
def test_a_lemma_splits_into_a_lexeme_and_a_pattern(
    lemma: str,
    part: PartOfSpeech,
    written: str,
    pattern: str,
) -> None:
    identifier = lexeme_id_from_lemma(part, lemma)
    assert identifier.part is part
    assert identifier.lemma == written
    assert identifier.pattern == pattern


def test_the_pattern_keeps_the_case_the_source_wrote() -> None:
    assert lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "zamek:Sm3~u").pattern == "Sm3~u"


@pytest.mark.parametrize(("lemma", "part", "written", "pattern"), LEMMA_CASES)
def test_a_token_round_trips(
    lemma: str,
    part: PartOfSpeech,
    written: str,
    pattern: str,
) -> None:
    identifier = lexeme_id_from_lemma(part, lemma)
    assert lexeme_id_from_token(token_of(identifier)) == identifier


def test_a_token_states_part_lemma_and_pattern() -> None:
    identifier = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "kot:Sm1")
    assert token_of(identifier) == "rzeczownik:KOT:Sm1"


def test_a_pattern_carrying_a_separator_round_trips() -> None:
    identifier = LexemeId(part=PartOfSpeech.RZECZOWNIK, lemma="KOT", pattern="Sm1:x")
    assert lexeme_id_from_token(token_of(identifier)) == identifier


def test_homonyms_of_one_lemma_stay_apart() -> None:
    castle = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "zamek:Sm3~u")
    zipper = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "zamek:Sm3~a")
    assert castle != zipper
    assert token_of(castle) != token_of(zipper)


def test_a_rescued_lexeme_stays_apart_from_a_patterned_one() -> None:
    rescued = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "kot")
    patterned = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "kot:Sm1")
    assert rescued != patterned


def test_one_lemma_under_two_parts_stays_apart() -> None:
    noun = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "broń")
    verb = lexeme_id_from_lemma(PartOfSpeech.CZASOWNIK, "bronić")
    assert noun != verb


def test_a_lexeme_identifier_keys_a_mapping() -> None:
    identifier = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "kot:Sm1")
    same = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "kot:Sm1")
    assert {identifier: "kot"}[same] == "kot"


def test_a_short_token_is_refused() -> None:
    with pytest.raises(InvalidConfiguration):
        lexeme_id_from_token("rzeczownik:KOT")


def test_a_token_naming_no_part_is_refused() -> None:
    with pytest.raises(ValueError):
        lexeme_id_from_token("zzz:KOT:Sm1")
