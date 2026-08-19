import marshal
import zipfile
from collections.abc import Iterable
from pathlib import Path

import pytest

from lexica import names as names_module
from lexica.compile import compile_lexicon, compile_morph_lexicon, load_compiled_lexicon
from lexica.morph.sources.sgjp import Interpretation
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.lexicon.morph import MorphLexicon
from wordtable import lexicons as lexicons_module
from wordtable import paths as paths_module

try:
    import morfeusz2  # type: ignore[import-untyped]
except ImportError:
    morfeusz2 = None

requires_morfeusz2 = pytest.mark.skipif(morfeusz2 is None, reason="morfeusz2 missing")


class ScriptedAnalyzer:
    def __init__(
        self,
        answers: dict[str, list[Interpretation]],
        generations: dict[str, list[Interpretation]] | None = None,
    ) -> None:
        self._answers = answers
        self._generations = generations if generations is not None else {}

    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]:
        return [(0, 1, interpretation) for interpretation in self._answers.get(text, [])]

    def generate(self, lemma: str) -> list[Interpretation]:
        return self._generations.get(lemma, [])

    def dict_id(self) -> str:
        return "scripted"


def _kot_analyzer() -> ScriptedAnalyzer:
    return ScriptedAnalyzer(
        answers={
            "kot": [("kot", "kot:Sm1", "subst:sg:nom:m1", ["nazwa_pospolita"], [])],
            "kota": [("kota", "kot:Sm1", "subst:sg:gen.acc:m1", ["nazwa_pospolita"], [])],
            "kotem": [("kotem", "kot:Sm1", "subst:sg:inst:m1", ["nazwa_pospolita"], [])],
            "kocie": [("kocie", "kot:Sm1", "subst:sg:loc:m1", ["nazwa_pospolita"], [])],
            "koty": [("koty", "kot:Sm1", "subst:pl:nom.acc.voc:m1", ["nazwa_pospolita"], [])],
            "aalborscy": [("aalborscy", "aalborski", "ign", [], [])],
        },
        generations={
            "kot:Sm1": [
                ("kot", "kot:Sm1", "subst:sg:nom:m1", ["nazwa_pospolita"], []),
                ("kota", "kot:Sm1", "subst:sg:gen.acc:m1", ["nazwa_pospolita"], []),
                ("kotów", "kot:Sm1", "subst:pl:gen:m1", ["nazwa_pospolita"], []),
            ]
        },
    )


def test_morph_lexicon_round_trip(tmp_path: Path) -> None:
    words = ("KOT", "KOTA", "KOTEM", "KOCIE", "KOTY", "AALBORSCY", "NIC")
    destination = tmp_path / "tiny.lexicon"
    compile_morph_lexicon(words, _kot_analyzer(), None, destination)
    lexicon = load_compiled_lexicon(destination)
    assert isinstance(lexicon, MorphLexicon)

    assert lexicon.judge("kot").allowed is True
    assert lexicon.judge("KOTEM").allowed is True
    assert lexicon.judge("aalborscy").allowed is True
    assert lexicon.judge("kotów").allowed is False
    assert lexicon.judge("xyz").allowed is False
    assert lexicon.has_prefix("ko") is True
    assert lexicon.has_prefix("xy") is False

    infos = lexicon.class_infos("kot")
    assert len(infos) == 1
    assert infos[0].class_id == "rzeczownik:KOT:SM1"
    assert infos[0].part == "rzeczownik"
    assert infos[0].base == "KOT"
    assert not lexicon.class_infos("aalborscy")
    assert not lexicon.class_infos("xyz")

    assert lexicon.unknown == ("AALBORSCY", "NIC")
    record = lexicon.classes["rzeczownik:KOT:SM1"]
    assert record.source == "sgjp"
    assert record.base == "KOT"
    variant_forms = record.variants[0::2]
    assert "KOTÓW" in variant_forms
    assert "KOTA" in variant_forms

    assert lexicon.analysis_rows("KOT") == (("KOT", "sgjp", "subst:sg:nom:m1"),)
    assert lexicon.analysis_rows("AALBORSCY") == ()
    assert lexicon.analysis_rows("xyz") == ()


def test_morph_lexicon_parity_with_text_lexicon(tmp_path: Path) -> None:
    words = ("KOT", "KOTA", "KOTEM", "KOCIE", "KOTY", "AALBORSCY", "NIC")
    destination = tmp_path / "tiny.lexicon"
    compile_morph_lexicon(words, _kot_analyzer(), None, destination)
    lexicon = load_compiled_lexicon(destination)
    text = TextLexicon.from_words(words)
    for word in (*words, "PIES", "KOTÓW"):
        assert lexicon.judge(word).allowed is text.judge(word).allowed, word
    for prefix in ("KO", "KOT", "PI", "AA"):
        assert lexicon.has_prefix(prefix) is text.has_prefix(prefix), prefix


def test_text_lexicon_round_trip(tmp_path: Path) -> None:
    destination = tmp_path / "text.lexicon"
    compile_lexicon(["kot", "KOTA", "dom"], destination)
    lexicon = load_compiled_lexicon(destination)
    assert isinstance(lexicon, TextLexicon)
    assert lexicon.words == ("DOM", "KOT", "KOTA")
    assert not lexicon.class_infos("kot")


def test_loader_rejects_malformed_payloads(tmp_path: Path) -> None:
    text_bad_surfaces = tmp_path / "bad1.lexicon"
    text_bad_surfaces.write_bytes(marshal.dumps(("literabble", 2, "nope")))
    with pytest.raises(InvalidConfiguration):
        load_compiled_lexicon(text_bad_surfaces)

    morph_dangling_class = tmp_path / "bad2.lexicon"
    morph_dangling_class.write_bytes(marshal.dumps(("literabble", 2, ("A",), (("x",),), {}, ())))
    with pytest.raises(InvalidConfiguration):
        load_compiled_lexicon(morph_dangling_class)

    morph_misaligned = tmp_path / "bad3.lexicon"
    morph_misaligned.write_bytes(marshal.dumps(("literabble", 2, ("A", "B"), (("x",),), {}, ())))
    with pytest.raises(InvalidConfiguration):
        load_compiled_lexicon(morph_misaligned)

    morph_bad_record = tmp_path / "bad4.lexicon"
    morph_bad_record.write_bytes(
        marshal.dumps(("literabble", 2, ("A",), (("x",),), {"x": ("a",)}, ()))
    )
    with pytest.raises(InvalidConfiguration):
        load_compiled_lexicon(morph_bad_record)

    stale = tmp_path / "bad5.lexicon"
    stale.write_bytes(marshal.dumps(("literabble", 1, ("A",))))
    with pytest.raises(InvalidConfiguration):
        load_compiled_lexicon(stale)


def test_compile_dictionary_dispatches_by_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    morph_calls: list[tuple[tuple[str, ...], Path | None, Path, object]] = []
    text_calls: list[tuple[tuple[str, ...], Path]] = []

    class _StubAnalyzer:
        def dict_id(self) -> str:
            return "stub"

    def fake_morph(
        words: tuple[str, ...],
        _analyzer: object,
        polimorf: Path | None,
        destination: Path,
        _overrides: object,
    ) -> None:
        morph_calls.append((words, polimorf, destination, _overrides))
        destination.write_bytes(b"")

    def fake_text(words: Iterable[str], destination: Path) -> None:
        text_calls.append((tuple(words), destination))
        destination.write_bytes(b"")

    monkeypatch.setattr(lexicons_module, "compile_morph_lexicon", fake_morph)
    monkeypatch.setattr(lexicons_module, "compile_lexicon", fake_text)
    monkeypatch.setattr(lexicons_module, "build_morfeusz_analyzer", lambda: _StubAnalyzer())
    monkeypatch.setattr(paths_module, "DICTIONARIES_DIR", tmp_path)

    with zipfile.ZipFile(tmp_path / "sjp-20260803.zip", "w") as archive:
        archive.writestr("slowa.txt", "kot\nkota\n")
    destination = lexicons_module.compile_dictionary(names_module.DictionaryName.SJP)
    words, polimorf, morph_destination, _ = morph_calls[0]
    assert words == ("KOT", "KOTA")
    assert polimorf is None
    assert destination == tmp_path / "sjp-20260803.v2.lexicon"
    assert morph_destination == destination

    destination_again = lexicons_module.compile_dictionary(names_module.DictionaryName.SJP)
    assert destination_again == destination
    assert len(morph_calls) == 1

    with zipfile.ZipFile(tmp_path / "english.zip", "w") as archive:
        archive.writestr("words.txt", "cat\ndog\n")
    destination = lexicons_module.compile_dictionary(names_module.DictionaryName.ENGLISH)
    words, text_destination = text_calls[0]
    assert destination == tmp_path / "english.v2.lexicon"
    assert text_destination == destination
    assert set(words) == {"CAT", "DOG"}


@requires_morfeusz2
def test_compile_with_real_analyzer(tmp_path: Path) -> None:
    words = ("BRONIĄ", "ZAMEK", "ZAMKA", "ZAMKU", "KOT", "KOTA")
    destination = tmp_path / "real.lexicon"
    compile_morph_lexicon(words, morfeusz2.Morfeusz(), None, destination)
    lexicon = load_compiled_lexicon(destination)
    assert isinstance(lexicon, MorphLexicon)

    bronia = lexicon.class_infos("BRONIĄ")
    assert len(bronia) == 2
    zamek = lexicon.class_infos("ZAMEK")
    assert len(zamek) == 2
    assert {info.base for info in zamek} == {"ZAMEK"}

    kot_record = lexicon.classes["rzeczownik:KOT:SM1"]
    variant_forms = kot_record.variants[0::2]
    assert "KOTÓW" in variant_forms
    assert not lexicon.class_infos("KOTÓW")
