import gzip
from pathlib import Path
from types import SimpleNamespace

import pytest

from lexica.grammar.gender import Gender
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.grammar.qualifier import Qualifier, QualifierKind
from lexica.lore.analysis import Analysis
from lexica.lore.analysis_source import AnalysisSource
from lexica.lore.rescue import RescueRow, rescued_analyses
from lexica.sources import sgjp
from lexica.sources.polimorf import rescue_rows
from lexica.sources.sgjp import Interpretation, analyse_word, generate_paradigm
from wordcore.errors.exceptions import InvalidConfiguration


class ScriptedAnalyzer:
    def __init__(self, answers: dict[str, list[Interpretation]]) -> None:
        self._answers = answers

    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]:
        return [(0, 1, interpretation) for interpretation in self._answers.get(text, [])]

    def generate(self, lemma: str) -> list[Interpretation]:
        return []

    def dict_id(self) -> str:
        return "scripted"


def test_analyse_word_filters_the_ign_reading() -> None:
    analyzer = ScriptedAnalyzer(
        {
            "bronią": [
                ("bronią", "broń", "subst:sg:inst:f", ["nazwa_pospolita"], []),
                ("bronią", "bronić", "fin:pl:ter:imperf", [], []),
                ("bronią", "bronić", "ign", [], []),
            ]
        }
    )
    analyses = analyse_word(analyzer, "BRONIĄ")
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
    analyses = analyse_word(analyzer, "MARSZ")
    assert analyses[0].qualifiers == (
        Qualifier(kind=QualifierKind.NAZWA, code="nazwa_pospolita"),
        Qualifier(kind=QualifierKind.KWALIFIKATOR, code="muz."),
    )
    assert analyses[0].lexeme.pattern == "Sm2.m3"


def test_analyse_word_splits_a_joined_label() -> None:
    analyzer = ScriptedAnalyzer({"czyżby": [("czyżby", "czyżby:T", "part", [], ["daw.,char."])]})
    analyses = analyse_word(analyzer, "CZYŻBY")
    assert analyses[0].qualifiers == (
        Qualifier(kind=QualifierKind.KWALIFIKATOR, code="daw."),
        Qualifier(kind=QualifierKind.KWALIFIKATOR, code="char."),
    )


class RecordingAnalyzer(ScriptedAnalyzer):
    def __init__(self) -> None:
        super().__init__({})
        self.asked: list[str] = []

    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]:
        self.asked.append(text)
        return super().analyse(text)


def test_analyse_word_asks_the_engine_in_lower_case() -> None:
    analyzer = RecordingAnalyzer()
    analyse_word(analyzer, "ŻÓŁWIA")
    assert analyzer.asked == ["żółwia"]


class SegmentedAnalyzer:
    def analyse(self, _text: str) -> list[tuple[int, int, Interpretation]]:
        return [
            (0, 1, ("biegł", "biec", "praet:sg:m1.m2.m3:imperf", [], [])),
            (1, 2, ("em", "być", "aglt:sg:pri:imperf:wok", [], [])),
        ]


def test_analyse_word_skips_movable_ending_segments() -> None:
    analyses = analyse_word(SegmentedAnalyzer(), "BIEGŁEM")
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
    analyses = analyse_word(MixedAnalyzer(), "CZYŻBY")
    assert [(analysis.lexeme.lemma, analysis.lexeme.pattern) for analysis in analyses] == [
        ("CZYŻBY", "I"),
        ("CZYŻBY", "T"),
    ]


class ScriptedGenerator:
    def __init__(self, paradigms: dict[str, list[Interpretation]]) -> None:
        self._paradigms = paradigms

    def analyse(self, _text: str) -> list[tuple[int, int, Interpretation]]:
        return []

    def generate(self, lemma: str) -> list[Interpretation]:
        return self._paradigms.get(lemma, [(lemma, lemma, "ign", [], [])])

    def dict_id(self) -> str:
        return sgjp.SGJP_DICTIONARY


def test_generate_paradigm_uppercases_every_form_it_keeps() -> None:
    generator = ScriptedGenerator(
        {
            "zamek:Sm3~a": [
                ("zamek", "zamek:Sm3~a", "subst:sg:nom.acc:m3", ["nazwa_pospolita"], []),
                ("zamka", "zamek:Sm3~a", "subst:sg:gen:m3", ["nazwa_pospolita"], []),
            ]
        }
    )
    assert generate_paradigm(generator, "zamek:Sm3~a") == (
        ("ZAMEK", "subst:sg:nom.acc:m3"),
        ("ZAMKA", "subst:sg:gen:m3"),
    )


def test_generate_paradigm_holds_no_form_for_a_lemma_the_engine_lacks() -> None:
    assert generate_paradigm(ScriptedGenerator({}), "abbozzo") == ()


def test_build_morfeusz_engine_refuses_a_dictionary_that_moved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class MovedEngine(ScriptedGenerator):
        def dict_id(self) -> str:
            return "pl.sgjp.sgjp-2027.01.01"

    monkeypatch.setattr(
        sgjp,
        "morfeusz2",
        SimpleNamespace(Morfeusz=lambda **_options: MovedEngine({})),
    )
    with pytest.raises(InvalidConfiguration, match=sgjp.SGJP_DICTIONARY):
        sgjp.build_morfeusz_engine()


def _write_polimorf(path: Path, rows: list[tuple[str, str, str, str, str]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("#!DICT-ID pl.waw.ipipan.polimorf-2026.07.27\r\n")
        handle.write("#<COPYRIGHT>\r\nPortions copyright 2026 the authors\r\n#</COPYRIGHT>\n")
        for form, lemma, tag, name, labels in rows:
            handle.write(f"{form}\t{lemma}\t{tag}\t{name}\t{labels}\n")


def _rescued(path: Path, targets: frozenset[str]) -> dict[str, tuple[Analysis, ...]]:
    return {
        surface: rescued_analyses(surface, rows)
        for surface, rows in rescue_rows(path, targets).items()
    }


def test_rescue_analyses_collects_and_dedupes_targets(tmp_path: Path) -> None:
    path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(
        path,
        [
            ("abadańscy", "abadański", "adj:pl:nom.voc:m1:pos", "nazwa_pospolita", ""),
            ("abadańscy", "abadański", "adj:pl:nom.voc:m1:pos", "nazwa_pospolita", ""),
            ("abbozzo", "abbozzo", "subst:sg:nom.acc.voc:n:ncol", "nazwa_pospolita", ""),
            ("niecelowy", "niecelowy", "adj:sg:nom:m3:pos", "nazwa_pospolita", ""),
        ],
    )
    rescued = _rescued(path, frozenset({"ABADAŃSCY", "ABBOZZO"}))
    assert set(rescued) == {"ABADAŃSCY", "ABBOZZO"}
    assert len(rescued["ABADAŃSCY"]) == 1
    analysis = rescued["ABBOZZO"][0]
    assert analysis.surface == "ABBOZZO"
    assert analysis.lexeme.lemma == "ABBOZZO"
    assert analysis.lexeme.part is PartOfSpeech.RZECZOWNIK
    assert analysis.source is AnalysisSource.POLIMORF
    assert analysis.qualifiers == (Qualifier(kind=QualifierKind.NAZWA, code="nazwa_pospolita"),)
    assert analysis.inflection.genders == frozenset({Gender.NIJAKI})


def test_rescue_analyses_reads_the_name_beside_the_qualifier(tmp_path: Path) -> None:
    path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(
        path,
        [("Abchazja", "Abchazja", "subst:sg:nom:f", "nazwa_geograficzna", "zwykle_lp")],
    )
    analysis = _rescued(path, frozenset({"ABCHAZJA"}))["ABCHAZJA"][0]
    assert analysis.qualifiers == (
        Qualifier(kind=QualifierKind.NAZWA, code="nazwa_geograficzna"),
        Qualifier(kind=QualifierKind.KWALIFIKATOR, code="zwykle_lp"),
    )
    assert analysis.inflection.genders == frozenset({Gender.ŻEŃSKI})


def test_rescue_analyses_reaches_a_capitalised_row(tmp_path: Path) -> None:
    path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(path, [("Abchazja", "Abchazja", "subst:sg:nom:f", "nazwa_geograficzna", "")])
    analysis = _rescued(path, frozenset({"ABCHAZJA"}))["ABCHAZJA"][0]
    assert analysis.surface == "ABCHAZJA"
    assert analysis.lexeme.lemma == "ABCHAZJA"


def test_rescue_analyses_passes_over_the_copyright_preamble(tmp_path: Path) -> None:
    path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(path, [])
    assert _rescued(path, frozenset({"AALBORSCY"})) == {}


def test_rescue_rows_hold_the_source_fields_a_reading_needs(tmp_path: Path) -> None:
    path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(
        path,
        [("Abchazja", "Abchazja", "subst:sg:nom:f", "nazwa_geograficzna", "zwykle_lp")],
    )
    assert rescue_rows(path, frozenset({"ABCHAZJA"})) == {
        "ABCHAZJA": (
            RescueRow(
                lemma="Abchazja",
                tag="subst:sg:nom:f",
                name="nazwa_geograficzna",
                label="zwykle_lp",
            ),
        )
    }
