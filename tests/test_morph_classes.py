import gzip
from pathlib import Path

from lexica.morph.classes import assemble_classes, lexeme_of, select_base
from lexica.morph.index import analyse_dictionary
from lexica.morph.mapping import build_analysis
from lexica.morph.models import Analysis, MorphSource
from lexica.morph.parts import PartOfSpeech
from lexica.morph.sources.sgjp import Interpretation


def _analysis(form: str, lemma: str, tag: str) -> Analysis:
    return build_analysis(form, lemma, tag, MorphSource.SGJP, ())


def test_assemble_classes_groups_variants_and_flags_dictionary_membership() -> None:
    analyses_by_form = {
        "KOT": (_analysis("KOT", "KOT:SM1", "subst:sg:nom:m1"),),
        "KOTA": (_analysis("KOTA", "KOT:SM1", "subst:sg:gen.acc:m1"),),
        "KOTEM": (_analysis("KOTEM", "KOT:SM1", "subst:sg:inst:m1"),),
        "KOCIE": (_analysis("KOCIE", "KOT:SM1", "subst:sg:loc:m1"),),
        "KOTY": (_analysis("KOTY", "KOT:SM1", "subst:pl:nom.acc.voc:m1"),),
    }
    dictionary = frozenset({"KOT", "KOTA", "KOTEM", "KOCIE", "KOTY"})
    generated = {
        "KOT:SM1": (
            ("KOT", "subst:sg:nom:m1"),
            ("KOTA", "subst:sg:gen.acc:m1"),
            ("KOTOWI", "subst:sg:dat:m1"),
            ("KOTEM", "subst:sg:inst:m1"),
            ("KOCIE", "subst:sg:loc:m1"),
            ("KOTY", "subst:pl:nom.acc.voc:m1"),
            ("KOTÓW", "subst:pl:gen:m1"),
        ),
    }
    store = assemble_classes(analyses_by_form, dictionary, generated)
    assert store.unknown == ()
    class_id = "rzeczownik:KOT:SM1"
    assert store.entries["KOT"] == (class_id,)
    record = store.classes[class_id]
    assert record.part is PartOfSpeech.RZECZOWNIK
    assert record.base == "KOT"
    forms = {variant.form for variant in record.variants}
    assert "KOTOWI" in forms
    assert "KOTÓW" in forms
    kotowi = next(variant for variant in record.variants if variant.form == "KOTOWI")
    assert kotowi.in_dictionary is False
    kot = next(variant for variant in record.variants if variant.form == "KOT")
    assert kot.in_dictionary is True


def test_homonym_forms_belong_to_several_classes() -> None:
    analyses_by_form = {
        "BRONIĄ": (
            _analysis("BRONIĄ", "BROŃ", "subst:sg:inst:f"),
            _analysis("BRONIĄ", "BRONIĆ", "fin:pl:ter:imperf"),
        ),
    }
    dictionary = frozenset({"BRONIĄ"})
    store = assemble_classes(analyses_by_form, dictionary, {})
    assert store.entries["BRONIĄ"] == ("czasownik:BRONIĆ", "rzeczownik:BROŃ")
    assert store.classes["rzeczownik:BROŃ"].base == "BROŃ"
    assert store.classes["czasownik:BRONIĆ"].base == "BRONIĆ"


def test_zamek_homonyms_keep_separate_classes() -> None:
    analyses_by_form = {
        "ZAMEK": (
            _analysis("ZAMEK", "ZAMEK:SM3~A", "subst:sg:nom.acc:m3"),
            _analysis("ZAMEK", "ZAMEK:SM3~U", "subst:sg:nom.acc:m3"),
        ),
        "ZAMKA": (_analysis("ZAMKA", "ZAMEK:SM3~A", "subst:sg:gen:m3"),),
        "ZAMKU": (_analysis("ZAMKU", "ZAMEK:SM3~U", "subst:sg:gen:m3"),),
    }
    store = assemble_classes(analyses_by_form, frozenset(analyses_by_form), {})
    assert set(store.entries["ZAMEK"]) == {
        "rzeczownik:ZAMEK:SM3~A",
        "rzeczownik:ZAMEK:SM3~U",
    }
    assert {record.base for record in store.classes.values()} == {"ZAMEK"}


def test_unknown_forms_pass_through() -> None:
    store = assemble_classes({"AALBORSCY": ()}, frozenset({"AALBORSCY"}), {})
    assert store.unknown == ("AALBORSCY",)
    assert store.entries == {}


def test_select_base_prefers_nominative_singular_for_nouns() -> None:
    variants = {"KOTEM": {"subst:sg:inst:m1"}, "KOT": {"subst:sg:nom:m1"}}
    assert select_base(PartOfSpeech.RZECZOWNIK, variants, "KOT") == "KOT"


def test_select_base_prefers_infinitive_for_verbs() -> None:
    variants = {"ROBIĘ": {"fin:sg:pri:imperf"}, "ROBIĆ": {"inf:imperf"}}
    assert select_base(PartOfSpeech.CZASOWNIK, variants, "ROBIĆ") == "ROBIĆ"


def test_select_base_falls_back_to_lexeme() -> None:
    variants = {"ROBIŁ": {"praet:sg:m1:imperf"}}
    assert select_base(PartOfSpeech.CZASOWNIK, variants, "ROBIĆ") == "ROBIĆ"


def test_select_base_adjective_prefers_masculine_nominative() -> None:
    variants = {
        "DROGA": {"adj:sg:nom.voc:f:pos"},
        "DROGI": {"adj:sg:nom:m1.m2.m3:pos"},
    }
    assert select_base(PartOfSpeech.PRZYMIOTNIK, variants, "DROGI") == "DROGI"


def test_select_base_uninflected_returns_lexeme() -> None:
    assert select_base(PartOfSpeech.PRZYSŁÓWEK, {}, "SZYBKO") == "SZYBKO"


def test_lexeme_of_strips_qualifiers() -> None:
    assert lexeme_of("BY:M") == "BY"
    assert lexeme_of("KOT:SM1") == "KOT"
    assert lexeme_of("ABBOZZO") == "ABBOZZO"


class ScriptedAnalyzer:
    def __init__(self, answers: dict[str, list[Interpretation]]) -> None:
        self._answers = answers

    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]:
        return [(0, 1, interpretation) for interpretation in self._answers.get(text, [])]

    def generate(self, lemma: str) -> list[Interpretation]:
        return []

    def dict_id(self) -> str:
        return "scripted"


def _write_polimorf(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for form, lemma, tag, qualifier in rows:
            handle.write(f"{form}\t{lemma}\t{tag}\t{qualifier}\n")


def test_analyse_dictionary_runs_sgjp_rescue_and_unknown(tmp_path: Path) -> None:
    polimorf_path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(
        polimorf_path,
        [("aalborscy", "aalborski", "adj:pl:nom.voc:m1.p1:pos", "pospolita")],
    )
    analyzer = ScriptedAnalyzer(
        answers={
            "kot": [("kot", "kot:Sm1", "subst:sg:nom:m1", ["nazwa_pospolita"], [])],
            "kota": [("kota", "kot:Sm1", "subst:sg:gen.acc:m1", ["nazwa_pospolita"], [])],
            "nic": [("nic", "nic", "ign", [], [])],
        },
    )
    words = ("KOT", "KOTA", "AALBORSCY", "NIC")
    result = analyse_dictionary(words, analyzer, polimorf_path)
    assert result.dict_id == "scripted"
    assert result.sgjp_classified == 2
    assert result.rescued == 1
    assert result.store.unknown == ("NIC",)
    assert "AALBORSCY" in result.store.entries
    assert "KOT" in {
        variant.form for variant in result.store.classes["rzeczownik:KOT:SM1"].variants
    }
