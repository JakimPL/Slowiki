from tests.fixtures.engines import scripted_sources

from lexica.build.coverage import CoverageResult, coverage_of
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.lore.override import OverrideRow
from lexica.lore.rescue import RescueRow
from lexica.names import DictionaryName
from wordtable.coverage import summary_of

ANSWERS = {
    "kot": [("kot", "kot:Sm1", "subst:sg:nom:m1", ["nazwa_pospolita"], [])],
    "kota": [("kota", "kot:Sm1", "subst:sg:gen.acc:m1", ["nazwa_pospolita"], [])],
    "bronią": [
        ("bronią", "broń:Sf", "subst:sg:inst:f", [], []),
        ("bronią", "bronić:V", "fin:pl:ter:imperf", [], []),
    ],
    "nic": [("nic", "nic", "ign", [], [])],
}

RESCUE = {
    "ABADAŃSCY": (
        RescueRow(lemma="abadański", tag="adj:pl:nom.voc:m1:pos", name="nazwa_pospolita", label=""),
    )
}

WORDS = ("KOT", "KOTA", "BRONIĄ", "ABADAŃSCY", "NIC")


def _coverage() -> CoverageResult:
    sources = scripted_sources(ANSWERS, {}, RESCUE)
    return coverage_of(DictionaryName.SJP, WORDS, sources)


def test_every_form_lands_in_exactly_one_bucket() -> None:
    coverage, _ = _coverage()
    assert coverage.forms == 5
    assert coverage.read == 3
    assert coverage.rescued == 1
    assert coverage.overridden == 0
    assert coverage.residual == 1
    assert (
        coverage.read + coverage.rescued + coverage.overridden + coverage.residual == coverage.forms
    )


def test_an_overridden_form_counts_as_its_own_bucket() -> None:
    overrides = {"NIC": (OverrideRow(lemma="NIC", tag="subst:sg:nom:n:ncol"),)}
    coverage, unread = coverage_of(
        DictionaryName.SJP,
        WORDS,
        scripted_sources(ANSWERS, {}, RESCUE, overrides),
    )
    assert coverage.read == 3
    assert coverage.rescued == 1
    assert coverage.overridden == 1
    assert coverage.residual == 0
    assert unread == ()


def test_the_residual_names_the_form_no_source_reads() -> None:
    _, unread = _coverage()
    assert unread == ("NIC",)


def test_the_report_counts_the_lexemes_the_sources_name() -> None:
    coverage, _ = _coverage()
    assert coverage.lexemes == 4
    assert coverage.parts == {
        PartOfSpeech.RZECZOWNIK: 2,
        PartOfSpeech.CZASOWNIK: 1,
        PartOfSpeech.PRZYMIOTNIK: 1,
    }


def test_the_report_carries_the_dictionary_it_read() -> None:
    coverage, _ = _coverage()
    assert coverage.dictionary is DictionaryName.SJP
    assert coverage.dict_id == "scripted"


def test_an_empty_dictionary_reports_no_share() -> None:
    coverage, unread = coverage_of(DictionaryName.SJP, (), scripted_sources({}, {}, {}))
    assert coverage.forms == 0
    assert unread == ()
    assert "read       0" in summary_of(coverage)


def test_the_summary_states_every_bucket_as_a_share() -> None:
    coverage, _ = _coverage()
    summary = summary_of(coverage)
    assert "5 forms read against scripted" in summary
    assert "read       3 (60.00%)" in summary
    assert "rescued    1 (20.00%)" in summary
    assert "overridden 0 (0.00%)" in summary
    assert "residual   1 (20.00%)" in summary
    assert "lexemes    4" in summary
