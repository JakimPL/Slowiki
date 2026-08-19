import gzip
from pathlib import Path

from lexica.grammar.gender import Gender
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.grammar.qualifier import Qualifier, QualifierKind
from lexica.lore.analysis_source import AnalysisSource
from lexica.sources.polimorf import rescue_analyses
from lexica.sources.sgjp import Interpretation, analyse_word


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
    assert noun.lexeme.lemma == "BROŃ"
    assert noun.lexeme.part is PartOfSpeech.RZECZOWNIK
    assert noun.qualifiers == (Qualifier(kind=QualifierKind.NAZWA, code="nazwa_pospolita"),)
    assert noun.source is AnalysisSource.SGJP


def test_analyse_word_types_names_apart_from_labels() -> None:
    analyzer = ScriptedAnalyzer(
        {
            "marsz": [
                ("marsz", "marsz:Sm2.m3", "subst:sg:nom.acc:m3", ["nazwa_pospolita"], ["muz."]),
            ]
        }
    )
    analyses = analyse_word(analyzer, "marsz")
    assert analyses[0].qualifiers == (
        Qualifier(kind=QualifierKind.NAZWA, code="nazwa_pospolita"),
        Qualifier(kind=QualifierKind.KWALIFIKATOR, code="muz."),
    )
    assert analyses[0].lexeme.pattern == "Sm2.m3"


def test_analyse_word_splits_a_joined_label() -> None:
    analyzer = ScriptedAnalyzer({"czyżby": [("czyżby", "czyżby:T", "part", [], ["daw.,char."])]})
    analyses = analyse_word(analyzer, "czyżby")
    assert analyses[0].qualifiers == (
        Qualifier(kind=QualifierKind.KWALIFIKATOR, code="daw."),
        Qualifier(kind=QualifierKind.KWALIFIKATOR, code="char."),
    )


class SegmentedAnalyzer:
    def analyse(self, _text: str) -> list[tuple[int, int, Interpretation]]:
        return [
            (0, 1, ("biegł", "biec", "praet:sg:m1.m2.m3:imperf", [], [])),
            (1, 2, ("em", "być", "aglt:sg:pri:imperf:wok", [], [])),
        ]


def test_analyse_word_skips_movable_ending_segments() -> None:
    analyses = analyse_word(SegmentedAnalyzer(), "biegłem")
    assert [analysis.lexeme.lemma for analysis in analyses] == ["BIEC"]
    assert [analysis.surface for analysis in analyses] == ["BIEGŁEM"]


class MixedAnalyzer:
    def analyse(self, _text: str) -> list[tuple[int, int, Interpretation]]:
        return [
            (0, 1, ("czyż", "czyż:T", "part", [], [])),
            (0, 2, ("czyżby", "czyżby:I", "interj", [], [])),
            (0, 2, ("czyżby", "czyżby:T", "part", [], [])),
            (1, 2, ("by", "by:T", "part", [], [])),
        ]


def test_analyse_word_prefers_full_word_over_segments() -> None:
    analyses = analyse_word(MixedAnalyzer(), "czyżby")
    assert [(analysis.lexeme.lemma, analysis.lexeme.pattern) for analysis in analyses] == [
        ("CZYŻBY", "I"),
        ("CZYŻBY", "T"),
    ]


def _write_polimorf(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for form, lemma, tag, category in rows:
            handle.write(f"{form}\t{lemma}\t{tag}\t{category}\n")


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
    assert analysis.lexeme.lemma == "ABBOZZO"
    assert analysis.lexeme.part is PartOfSpeech.RZECZOWNIK
    assert analysis.source is AnalysisSource.POLIMORF
    assert analysis.qualifiers == (Qualifier(kind=QualifierKind.NAZWA, code="pospolita"),)
    assert analysis.inflection.genders == frozenset({Gender.NIJAKI})


def test_rescue_analyses_reads_the_plural_gender_the_old_tagset_wrote(tmp_path: Path) -> None:
    path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(
        path,
        [("abadańscy", "abadański", "adj:pl:nom.voc:m1.p1:pos", "pospolita")],
    )
    analysis = rescue_analyses(path, frozenset({"abadańscy"}))["abadańscy"][0]
    assert analysis.inflection.genders == frozenset({Gender.MĘSKOOSOBOWY})


def test_rescue_analyses_returns_nothing_for_empty_targets(tmp_path: Path) -> None:
    path = tmp_path / "empty.tab.gz"
    _write_polimorf(path, [])
    assert rescue_analyses(path, frozenset({"aalborscy"})) == {}
