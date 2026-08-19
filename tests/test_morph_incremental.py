import gzip
from pathlib import Path

import pytest

from lexica.compile import compile_morph_lexicon, load_compiled_lexicon
from lexica.morph.diff import diff_lexicons
from lexica.morph.manifest import compile_input_digests, load_manifest, write_manifest
from lexica.morph.overrides import parse_overrides
from lexica.morph.report import build_artifact_report
from lexica.morph.sources.sgjp import Interpretation
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.lexicon.morph import MorphLexicon


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
            "kocie": [("kocie", "kot:Sm1", "subst:sg:loc:m1", ["nazwa_pospolita"], [])],
        },
    )


def _write_polimorf(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for form, lemma, tag, qualifier in rows:
            handle.write(f"{form}\t{lemma}\t{tag}\t{qualifier}\n")


def test_compile_is_byte_identical_on_rerun(tmp_path: Path) -> None:
    words = ("KOT", "KOTA", "KOCIE", "AALBORSCY")
    first = tmp_path / "first.lexicon"
    second = tmp_path / "second.lexicon"
    compile_morph_lexicon(words, _kot_analyzer(), None, first)
    compile_morph_lexicon(words, _kot_analyzer(), None, second)
    assert first.read_bytes() == second.read_bytes()


def test_overrides_replace_analyses(tmp_path: Path) -> None:
    words = ("KOT", "KOTA", "AALBORSCY")
    destination = tmp_path / "tiny.lexicon"
    compile_morph_lexicon(
        words,
        _kot_analyzer(),
        None,
        destination,
        {"KOTA": (("KOT:SM1", "subst:sg:nom:m1"),)},
    )
    lexicon = load_compiled_lexicon(destination)
    assert isinstance(lexicon, MorphLexicon)
    assert lexicon.analysis_rows("KOTA") == (("KOT", "sgjp", "subst:sg:nom:m1"),)


def test_override_removal_forces_unknown(tmp_path: Path) -> None:
    words = ("KOT", "AALBORSCY")
    destination = tmp_path / "tiny.lexicon"
    compile_morph_lexicon(words, _kot_analyzer(), None, destination, {"KOT": ()})
    lexicon = load_compiled_lexicon(destination)
    assert isinstance(lexicon, MorphLexicon)
    assert lexicon.unknown == ("AALBORSCY", "KOT")
    assert not lexicon.class_infos("KOT")


def test_overrides_skip_polimorf_rescue(tmp_path: Path) -> None:
    polimorf = tmp_path / "polimorf.tab.gz"
    _write_polimorf(
        polimorf,
        [("aalborscy", "aalborski", "adj:pl:nom.voc:m1.p1:pos", "pospolita")],
    )
    words = ("KOT", "AALBORSCY")

    rescued_destination = tmp_path / "rescued.lexicon"
    compile_morph_lexicon(words, _kot_analyzer(), polimorf, rescued_destination)
    rescued = load_compiled_lexicon(rescued_destination)
    assert isinstance(rescued, MorphLexicon)
    assert rescued.unknown == ()
    assert len(rescued.class_infos("AALBORSCY")) == 1
    assert build_artifact_report(rescued).polimorf_classes == 1

    forced_destination = tmp_path / "forced.lexicon"
    compile_morph_lexicon(
        words,
        _kot_analyzer(),
        polimorf,
        forced_destination,
        {"AALBORSCY": ()},
    )
    forced = load_compiled_lexicon(forced_destination)
    assert isinstance(forced, MorphLexicon)
    assert forced.unknown == ("AALBORSCY",)


def test_parse_overrides_validates_forms(tmp_path: Path) -> None:
    path = tmp_path / "overrides.morph.yaml"
    path.write_text(
        "overrides:\n"
        "  - form: kot\n"
        "    analyses:\n"
        "      - lemma: kot:Sm1\n"
        "        tag: subst:sg:nom:m1\n",
        encoding="utf-8",
    )
    overrides = parse_overrides(path, frozenset({"KOT"}))
    assert overrides == {"KOT": (("KOT:SM1", "subst:sg:nom:m1"),)}

    path.write_text(
        "overrides:\n  - form: nieznane\n    analyses: []\n",
        encoding="utf-8",
    )
    with pytest.raises(InvalidConfiguration):
        parse_overrides(path, frozenset({"KOT"}))


def test_manifest_round_trip(tmp_path: Path) -> None:
    archive = tmp_path / "sjp.zip"
    archive.write_bytes(b"abc")
    digests = compile_input_digests(archive, None, None, "dict", 1, 2)
    manifest = tmp_path / "manifest.json"
    write_manifest(manifest, digests)
    assert load_manifest(manifest) == digests
    assert load_manifest(tmp_path / "missing.json") == {}


def test_diff_reports_surface_and_class_changes(tmp_path: Path) -> None:
    old_path = tmp_path / "old.lexicon"
    new_path = tmp_path / "new.lexicon"
    compile_morph_lexicon(("KOT", "KOTA"), _kot_analyzer(), None, old_path)
    compile_morph_lexicon(("KOT", "KOCIE"), _kot_analyzer(), None, new_path)
    old = load_compiled_lexicon(old_path)
    new = load_compiled_lexicon(new_path)
    assert isinstance(old, MorphLexicon)
    assert isinstance(new, MorphLexicon)

    change = diff_lexicons(old, new)
    assert change.surfaces_added == ("KOCIE",)
    assert change.surfaces_removed == ("KOTA",)
    assert change.classes_added == ()
    assert change.classes_removed == ()
    assert change.classes_changed == ("rzeczownik:KOT:SM1",)


def test_artifact_report_counts(tmp_path: Path) -> None:
    destination = tmp_path / "tiny.lexicon"
    compile_morph_lexicon(("KOT", "KOTA", "AALBORSCY"), _kot_analyzer(), None, destination)
    lexicon = load_compiled_lexicon(destination)
    assert isinstance(lexicon, MorphLexicon)
    report = build_artifact_report(lexicon)
    assert report.total_forms == 3
    assert report.unknown == 1
    assert report.class_count == 1
    assert report.multi_class_forms == 0
    assert report.classes_per_part == {"rzeczownik": 1}
