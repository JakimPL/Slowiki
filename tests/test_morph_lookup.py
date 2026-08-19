from lexica.morph.lookup import lookup_lines
from wordcore.lexicon.morph import MorphClass, MorphLexicon


def _bronia_lexicon() -> MorphLexicon:
    return MorphLexicon(
        surfaces=("AALBORSCY", "BRONIĄ", "KOT", "KOTA"),
        entries=(
            (),
            ("czasownik:BRONIĆ", "rzeczownik:BROŃ"),
            ("rzeczownik:KOT:SM1",),
            ("rzeczownik:KOT:SM1",),
        ),
        classes={
            "czasownik:BRONIĆ": MorphClass(
                class_id="czasownik:BRONIĆ",
                part="czasownik",
                lemma="BRONIĆ",
                base="BRONIĆ",
                source="sgjp",
                variants=("BRONIĄ", "fin:pl:ter:imperf"),
            ),
            "rzeczownik:BROŃ": MorphClass(
                class_id="rzeczownik:BROŃ",
                part="rzeczownik",
                lemma="BROŃ",
                base="BROŃ",
                source="sgjp",
                variants=("BRONIĄ", "subst:sg:inst:f"),
            ),
            "rzeczownik:KOT:SM1": MorphClass(
                class_id="rzeczownik:KOT:SM1",
                part="rzeczownik",
                lemma="KOT",
                base="KOT",
                source="sgjp",
                variants=(
                    "KOT",
                    "subst:sg:nom:m1",
                    "KOTA",
                    "subst:sg:gen.acc:m1",
                ),
            ),
        },
        unknown=("AALBORSCY",),
    )


def test_lookup_lists_every_analysis_of_a_homonym() -> None:
    lines = lookup_lines(_bronia_lexicon(), "bronią")
    assert lines[0] == "BRONIĄ"
    assert "  czasownik · BRONIĆ · fin:pl:ter:imperf" in lines
    assert "  rzeczownik · BROŃ · subst:sg:inst:f" in lines
    assert any("osoba: trzecia" in line for line in lines)
    assert any("przypadki: narzędnik" in line for line in lines)


def test_lookup_describes_grammatical_tags() -> None:
    lines = lookup_lines(_bronia_lexicon(), "kota")
    assert lines[0] == "KOTA"
    assert "  rzeczownik · KOT · subst:sg:gen.acc:m1" in lines
    assert any("przypadki: biernik, dopełniacz" in line for line in lines)
    assert any("liczba: pojedyncza" in line for line in lines)
    assert any("rodzaje: męskoosobowy" in line for line in lines)


def test_lookup_reports_unknown_and_absent_words() -> None:
    lexicon = _bronia_lexicon()
    assert lookup_lines(lexicon, "xyzzydom") == ("XYZZYDOM: absent from the dictionary",)
    assert lookup_lines(lexicon, "aalborscy") == ("AALBORSCY: unclassified",)
