import gzip
from pathlib import Path

from lexica.build.assemble import assemble_classes, select_base
from lexica.build.orchestrate import analyse_dictionary
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.lore.analysis import Analysis, analysis_of
from lexica.lore.analysis_source import AnalysisSource
from lexica.lore.lexeme_id import LexemeId, lexeme_id_from_lemma, token_of
from lexica.sources.sgjp import Interpretation

KOT = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "KOT:Sm1")


def _analysis(form: str, lemma: str, tag: str) -> Analysis:
    return analysis_of(form, lemma, tag, AnalysisSource.SGJP, (), ())


def test_assemble_classes_groups_variants_and_flags_dictionary_membership() -> None:
    analyses_by_form = {
        "KOT": (_analysis("KOT", "KOT:Sm1", "subst:sg:nom:m1"),),
        "KOTA": (_analysis("KOTA", "KOT:Sm1", "subst:sg:gen.acc:m1"),),
        "KOTEM": (_analysis("KOTEM", "KOT:Sm1", "subst:sg:inst:m1"),),
        "KOCIE": (_analysis("KOCIE", "KOT:Sm1", "subst:sg:loc:m1"),),
        "KOTY": (_analysis("KOTY", "KOT:Sm1", "subst:pl:nom.acc.voc:m1"),),
    }
    dictionary = frozenset({"KOT", "KOTA", "KOTEM", "KOCIE", "KOTY"})
    generated = {
        KOT: (
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
    assert store.entries["KOT"] == (KOT,)
    record = store.classes[KOT]
    assert record.lexeme.part is PartOfSpeech.RZECZOWNIK
    assert record.base == "KOT"
    forms = {variant.form for variant in record.variants}
    assert "KOTOWI" in forms
    assert "KOTÓW" in forms
    kotowi = next(variant for variant in record.variants if variant.form == "KOTOWI")
    assert kotowi.in_dictionary is False
    kot = next(variant for variant in record.variants if variant.form == "KOT")
    assert kot.in_dictionary is True


def test_generated_forms_reach_no_lexeme_of_their_own() -> None:
    unseen = lexeme_id_from_lemma(PartOfSpeech.RZECZOWNIK, "PIES:Sm2")
    store = assemble_classes(
        {"KOT": (_analysis("KOT", "KOT:Sm1", "subst:sg:nom:m1"),)},
        frozenset({"KOT"}),
        {unseen: (("PSA", "subst:sg:gen:m2"),)},
    )
    assert set(store.classes) == {KOT}


def test_every_variant_carries_the_source_that_read_it() -> None:
    store = assemble_classes(
        {"KOT": (_analysis("KOT", "KOT:Sm1", "subst:sg:nom:m1"),)},
        frozenset({"KOT"}),
        {KOT: (("KOTOWI", "subst:sg:dat:m1"),)},
    )
    sources = {variant.source for variant in store.classes[KOT].variants}
    assert sources == {AnalysisSource.SGJP}


def test_homonym_forms_belong_to_several_classes() -> None:
    analyses_by_form = {
        "BRONIĄ": (
            _analysis("BRONIĄ", "BROŃ", "subst:sg:inst:f"),
            _analysis("BRONIĄ", "BRONIĆ", "fin:pl:ter:imperf"),
        ),
    }
    store = assemble_classes(analyses_by_form, frozenset({"BRONIĄ"}), {})
    tokens = tuple(token_of(lexeme) for lexeme in store.entries["BRONIĄ"])
    assert tokens == ("czasownik:BRONIĆ:", "rzeczownik:BROŃ:")
    for lexeme in store.entries["BRONIĄ"]:
        assert store.classes[lexeme].base == lexeme.lemma


def test_zamek_homonyms_keep_separate_classes() -> None:
    analyses_by_form = {
        "ZAMEK": (
            _analysis("ZAMEK", "ZAMEK:Sm3~a", "subst:sg:nom.acc:m3"),
            _analysis("ZAMEK", "ZAMEK:Sm3~u", "subst:sg:nom.acc:m3"),
        ),
        "ZAMKA": (_analysis("ZAMKA", "ZAMEK:Sm3~a", "subst:sg:gen:m3"),),
        "ZAMKU": (_analysis("ZAMKU", "ZAMEK:Sm3~u", "subst:sg:gen:m3"),),
    }
    store = assemble_classes(analyses_by_form, frozenset(analyses_by_form), {})
    assert {token_of(lexeme) for lexeme in store.entries["ZAMEK"]} == {
        "rzeczownik:ZAMEK:Sm3~a",
        "rzeczownik:ZAMEK:Sm3~u",
    }
    assert {record.base for record in store.classes.values()} == {"ZAMEK"}


def test_an_sgjp_lexeme_never_merges_with_a_rescued_one() -> None:
    analyses_by_form = {
        "KOT": (_analysis("KOT", "KOT:Sm1", "subst:sg:nom:m1"),),
        "KOTA": (analysis_of("KOTA", "kot", "subst:sg:gen:m1", AnalysisSource.POLIMORF, (), ()),),
    }
    store = assemble_classes(analyses_by_form, frozenset(analyses_by_form), {})
    assert len(store.classes) == 2
    assert {lexeme.pattern for lexeme in store.classes} == {"Sm1", ""}


def test_unknown_forms_pass_through() -> None:
    store = assemble_classes({"AALBORSCY": ()}, frozenset({"AALBORSCY"}), {})
    assert store.unknown == ("AALBORSCY",)
    assert store.entries == {}


def _variants(readings: dict[str, tuple[str, ...]]) -> dict[str, frozenset[tuple[str, str]]]:
    return {
        form: frozenset((tag, AnalysisSource.SGJP) for tag in tags)
        for form, tags in readings.items()
    }


def test_select_base_prefers_nominative_singular_for_nouns() -> None:
    variants = _variants({"KOTEM": ("subst:sg:inst:m1",), "KOT": ("subst:sg:nom:m1",)})
    assert select_base(KOT, variants) == "KOT"


def test_select_base_prefers_infinitive_for_verbs() -> None:
    robic = lexeme_id_from_lemma(PartOfSpeech.CZASOWNIK, "ROBIĆ")
    variants = _variants({"ROBIĘ": ("fin:sg:pri:imperf",), "ROBIĆ": ("inf:imperf",)})
    assert select_base(robic, variants) == "ROBIĆ"


def test_select_base_falls_back_to_the_lemma() -> None:
    robic = lexeme_id_from_lemma(PartOfSpeech.CZASOWNIK, "ROBIĆ")
    assert select_base(robic, _variants({"ROBIŁ": ("praet:sg:m1:imperf",)})) == "ROBIĆ"


def test_select_base_adjective_prefers_masculine_nominative() -> None:
    drogi = lexeme_id_from_lemma(PartOfSpeech.PRZYMIOTNIK, "DROGI")
    variants = _variants(
        {
            "DROGA": ("adj:sg:nom.voc:f:pos",),
            "DROGI": ("adj:sg:nom:m1.m2.m3:pos",),
        }
    )
    assert select_base(drogi, variants) == "DROGI"


def test_select_base_uninflected_returns_the_lemma() -> None:
    szybko = lexeme_id_from_lemma(PartOfSpeech.PRZYSŁÓWEK, "SZYBKO")
    assert select_base(szybko, {}) == "SZYBKO"


def test_select_base_reads_a_rescued_form() -> None:
    abadanski = lexeme_id_from_lemma(PartOfSpeech.PRZYMIOTNIK, "ABADAŃSKI")
    variants = {
        "ABADAŃSCY": frozenset({("adj:pl:nom.voc:m1:pos", AnalysisSource.POLIMORF)}),
        "ABADAŃSKI": frozenset({("adj:sg:nom:m1:pos", AnalysisSource.POLIMORF)}),
    }
    assert select_base(abadanski, variants) == "ABADAŃSKI"


class ScriptedAnalyzer:
    def __init__(
        self,
        answers: dict[str, list[Interpretation]],
        paradigms: dict[str, list[Interpretation]],
    ) -> None:
        self._answers = answers
        self._paradigms = paradigms

    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]:
        return [(0, 1, interpretation) for interpretation in self._answers.get(text, [])]

    def generate(self, lemma: str) -> list[Interpretation]:
        return self._paradigms.get(lemma, [(lemma, lemma, "ign", [], [])])

    def dict_id(self) -> str:
        return "scripted"


def _write_polimorf(path: Path, rows: list[tuple[str, str, str, str, str]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for form, lemma, tag, name, labels in rows:
            handle.write(f"{form}\t{lemma}\t{tag}\t{name}\t{labels}\n")


def test_analyse_dictionary_runs_sgjp_rescue_and_unknown(tmp_path: Path) -> None:
    polimorf_path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(
        polimorf_path,
        [("aalborscy", "aalborski", "adj:pl:nom.voc:m1:pos", "nazwa_pospolita", "")],
    )
    analyzer = ScriptedAnalyzer(
        answers={
            "kot": [("kot", "kot:Sm1", "subst:sg:nom:m1", ["nazwa_pospolita"], [])],
            "kota": [("kota", "kot:Sm1", "subst:sg:gen.acc:m1", ["nazwa_pospolita"], [])],
            "nic": [("nic", "nic", "ign", [], [])],
        },
        paradigms={},
    )
    words = ("KOT", "KOTA", "AALBORSCY", "NIC")
    result = analyse_dictionary(words, analyzer, polimorf_path)
    assert result.dict_id == "scripted"
    assert result.sgjp_classified == 2
    assert result.rescued == 1
    assert result.store.unknown == ("NIC",)
    assert "AALBORSCY" in result.store.entries
    assert "KOT" in {variant.form for variant in result.store.classes[KOT].variants}


def test_analyse_dictionary_carries_the_generated_paradigm() -> None:
    analyzer = ScriptedAnalyzer(
        answers={"kot": [("kot", "kot:Sm1", "subst:sg:nom:m1", ["nazwa_pospolita"], [])]},
        paradigms={
            "kot:Sm1": [
                ("kot", "kot:Sm1", "subst:sg:nom:m1", ["nazwa_pospolita"], []),
                ("kotowi", "kot:Sm1", "subst:sg:dat:m1", ["nazwa_pospolita"], []),
            ]
        },
    )
    result = analyse_dictionary(("KOT",), analyzer, None)
    variants = {
        variant.form: variant.in_dictionary for variant in result.store.classes[KOT].variants
    }
    assert variants == {"KOT": True, "KOTOWI": False}


def test_a_rescued_lexeme_carries_the_forms_the_source_holds(tmp_path: Path) -> None:
    polimorf_path = tmp_path / "polimorf.tab.gz"
    _write_polimorf(
        polimorf_path,
        [("aalborscy", "aalborski", "adj:pl:nom.voc:m1:pos", "nazwa_pospolita", "")],
    )
    analyzer = ScriptedAnalyzer(
        answers={},
        paradigms={"aalborski": [("aalborski", "aalborski", "adj:sg:nom:m1:pos", [], [])]},
    )
    result = analyse_dictionary(("AALBORSCY",), analyzer, polimorf_path)
    lexeme = result.store.entries["AALBORSCY"][0]
    assert {variant.form for variant in result.store.classes[lexeme].variants} == {"AALBORSCY"}


def test_a_lexeme_identifier_keys_the_store() -> None:
    store = assemble_classes(
        {"KOT": (_analysis("KOT", "KOT:Sm1", "subst:sg:nom:m1"),)},
        frozenset({"KOT"}),
        {},
    )
    assert isinstance(next(iter(store.classes)), LexemeId)
