import gzip
from pathlib import Path

from lexica.morph.models import MorphSource
from lexica.morph.parts import PartOfSpeech
from lexica.morph.sources.polimorf import rescue_analyses
from lexica.morph.sources.sgjp import Interpretation, analyse_word, analyse_word_entries
from lexica.morph.tags import Gender


class ScriptedAnalyzer:
    def __init__(self, answers: dict[str, list[Interpretation]]) -> None:
        self._answers = answers

    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]:
        return [(0, 1, interpretation) for interpretation in self._answers.get(text, [])]

    def generate(self, lemma: str) -> list[Interpretation]:
        return []

    def dict_id(self) -> str:
        return "scripted"


def test_analyse_word_filters_ign_and_uppercases() -> None:
    analyzer = ScriptedAnalyzer(
        {
            "bronią": [
                ("bronią", "broń", "subst:sg:inst:f", ["nazwa_pospolita"], []),
                ("bronią", "bronić", "fin:pl:ter:imperf", [], []),
                ("bronią", "bronić", "ign", [], []),
            ]
        }
    )
    analyses = analyse_word(analyzer, "bronią")
    assert len(analyses) == 2
    noun = analyses[0]
    assert noun.surface == "BRONIĄ"
    assert noun.lemma == "BROŃ"
    assert noun.part is PartOfSpeech.RZECZOWNIK
    assert noun.qualifiers == ("nazwa_pospolita",)
    assert noun.source is MorphSource.SGJP


def test_analyse_word_merges_names_with_qualifiers() -> None:
    analyzer = ScriptedAnalyzer(
        {
            "marsz": [
                ("marsz", "marsz:Sm2.m3", "subst:sg:nom.acc:m3", ["nazwa_pospolita"], ["muz."]),
            ]
        }
    )
    analyses = analyse_word(analyzer, "marsz")
    assert analyses[0].qualifiers == ("nazwa_pospolita", "muz.")


def test_analyse_word_entries_keeps_original_lemma_case() -> None:
    analyzer = ScriptedAnalyzer({"kot": [("kot", "kot:Sm1", "subst:sg:nom:m1", [], [])]})
    entries = analyse_word_entries(analyzer, "kot")
    assert entries == (("KOT:SM1", "kot:Sm1", "subst:sg:nom:m1"),)


def _write_polimorf(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for form, lemma, tag, qualifier in rows:
            handle.write(f"{form}\t{lemma}\t{tag}\t{qualifier}\n")


def test_rescue_analyses_collects_and_dedupes_targets(tmp_path: Path) -> None:
    path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(
        path,
        [
            ("abadańscy", "abadański", "adj:pl:nom.voc:m1.p1:pos", "pospolita"),
            ("abadańscy", "abadański", "adj:pl:nom.voc:m1.p1:pos", "pospolita"),
            ("abbozzo", "abbozzo", "subst:sg:nom:n2", "pospolita"),
            ("niecelowy", "niecelowy", "adj:sg:nom:m3:pos", "pospolita"),
        ],
    )
    rescued = rescue_analyses(path, frozenset({"abadańscy", "abbozzo"}))
    assert set(rescued) == {"abadańscy", "abbozzo"}
    assert len(rescued["abadańscy"]) == 1
    analysis = rescued["abbozzo"][0]
    assert analysis.surface == "ABBOZZO"
    assert analysis.lemma == "ABBOZZO"
    assert analysis.part is PartOfSpeech.RZECZOWNIK
    assert analysis.source is MorphSource.POLIMORF
    assert analysis.qualifiers == ("pospolita",)
    assert analysis.tags.genders == frozenset({Gender.NIJAKI})


def test_rescue_analyses_returns_nothing_for_empty_targets(tmp_path: Path) -> None:
    path = tmp_path / "empty.tab.gz"
    _write_polimorf(path, [])
    assert rescue_analyses(path, frozenset({"aalborscy"})) == {}
