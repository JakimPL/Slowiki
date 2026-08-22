from collections import Counter
from itertools import permutations
from pathlib import Path

import pytest
from tests.fixtures.oracle import Oracle, ReadingClaim, Specimen, read_oracle

from lexica.lore.lookup import lore_of
from lexica.lore.reading import LoreReading, WordLore
from lexica.lore.sources import LoreSources
from lexica.sources.sgjp import build_morfeusz_engine
from wordcore.lexicon.lexicon import TextLexicon

try:
    import morfeusz2  # type: ignore[import-untyped]
except ImportError:
    morfeusz2 = None

ORACLE_PATH = Path(__file__).resolve().parent / "specimens" / "oracle.yaml"

requires_morfeusz2 = pytest.mark.skipif(morfeusz2 is None, reason="morfeusz2 missing")
requires_oracle = pytest.mark.skipif(not ORACLE_PATH.is_file(), reason="oracle missing")


@pytest.fixture(scope="module", name="oracle")
def oracle_fixture() -> Oracle:
    return read_oracle(ORACLE_PATH)


@pytest.fixture(scope="module", name="answers")
def answers_fixture(oracle: Oracle) -> dict[str, WordLore]:
    words = tuple(specimen.word for specimen in oracle.specimens)
    sources = LoreSources(engine=build_morfeusz_engine(), rescue={})
    lexicon = TextLexicon.from_words(words)
    return {word: lore_of(sources, word, lexicon) for word in words}


@requires_oracle
def test_the_oracle_names_every_specimen_once(oracle: Oracle) -> None:
    words = [specimen.word for specimen in oracle.specimens]
    assert len(words) == len(set(words))
    assert words == sorted(words)


@requires_morfeusz2
@requires_oracle
def test_the_oracle_pins_the_analysed_dictionary(oracle: Oracle) -> None:
    assert build_morfeusz_engine().dict_id() == oracle.dict_id


@requires_morfeusz2
@requires_oracle
def test_every_specimen_reads_into_the_claimed_lexemes(
    oracle: Oracle, answers: dict[str, WordLore]
) -> None:
    for specimen in oracle.specimens:
        claimed = Counter(claim.lexeme for claim in specimen.readings)
        read = Counter((reading.part, reading.base) for reading in answers[specimen.word].readings)
        assert claimed - read == Counter(), f"{specimen.word} misses {sorted(claimed - read)}"


@requires_morfeusz2
@requires_oracle
def test_no_specimen_reads_into_a_lexeme_the_oracle_denies(
    oracle: Oracle, answers: dict[str, WordLore]
) -> None:
    for specimen in oracle.specimens:
        read = {(reading.part, reading.base) for reading in answers[specimen.word].readings}
        denied = {denial.lexeme for denial in specimen.denied}
        assert read.isdisjoint(denied), f"{specimen.word} reads into {sorted(read & denied)}"


@requires_morfeusz2
@requires_oracle
def test_an_unread_specimen_earns_no_reading(oracle: Oracle, answers: dict[str, WordLore]) -> None:
    for specimen in oracle.specimens:
        if len(specimen.readings) > 0:
            continue
        assert answers[specimen.word].readings == (), specimen.word


@requires_morfeusz2
@requires_oracle
def test_every_specimen_carries_the_claimed_grammar(
    oracle: Oracle, answers: dict[str, WordLore]
) -> None:
    for specimen in oracle.specimens:
        for lexeme, claims in _claims_by_lexeme(specimen).items():
            readings = _readings_of(answers[specimen.word], lexeme)
            assert _assignment_exists(specimen, claims, readings), f"{specimen.word} {lexeme}"


@requires_morfeusz2
@requires_oracle
def test_no_specimen_invents_a_form_the_oracle_denies(
    oracle: Oracle, answers: dict[str, WordLore]
) -> None:
    for specimen in oracle.specimens:
        produced = {
            form.text for reading in answers[specimen.word].readings for form in reading.forms
        }
        assert produced.isdisjoint(specimen.absent), specimen.word


def _claims_by_lexeme(specimen: Specimen) -> dict[tuple[str, str], list[ReadingClaim]]:
    grouped: dict[tuple[str, str], list[ReadingClaim]] = {}
    for claim in specimen.readings:
        grouped.setdefault(claim.lexeme, []).append(claim)
    return grouped


def _readings_of(answer: WordLore, lexeme: tuple[str, str]) -> list[LoreReading]:
    return [reading for reading in answer.readings if (reading.part, reading.base) == lexeme]


def _assignment_exists(
    specimen: Specimen, claims: list[ReadingClaim], readings: list[LoreReading]
) -> bool:
    return any(
        all(_claim_holds(specimen, claim, reading) for claim, reading in zip(claims, order))
        for order in permutations(readings, len(claims))
    )


def _claim_holds(specimen: Specimen, claim: ReadingClaim, reading: LoreReading) -> bool:
    return _surface_holds(specimen, claim, reading) and _contains_holds(claim, reading)


def _surface_holds(specimen: Specimen, claim: ReadingClaim, reading: LoreReading) -> bool:
    if claim.surface is None:
        return True

    return any(
        claim.surface.holds_for(form.tags) for form in reading.forms if form.text == specimen.word
    )


def _contains_holds(claim: ReadingClaim, reading: LoreReading) -> bool:
    return set(claim.contains) <= {form.text for form in reading.forms}
