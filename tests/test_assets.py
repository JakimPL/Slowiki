import json
import re

from wordassets.board import SPECIMEN_WORDS, board_specimen
from wordassets.build import build_assets
from wordassets.colors import mixed_hex
from wordassets.drawing.node import Element, document, rendered
from wordassets.drawing.shapes import polygon, rect
from wordassets.geometry import star_points
from wordassets.slugs import letter_slug
from wordgames.names import GameName
from wordtable.catalogue import resolve_scheme
from wordtable.config import ThemeTokens, load_style_tokens
from wordtable.paths import CONFIG_DIR


def test_rendered_escapes_markup() -> None:
    element = Element(
        tag="text",
        attributes=(("data-note", 'say "hi" & <run>'),),
        children=(),
        text="a < b & c",
    )
    markup = rendered(element)
    assert "data-note='say \"hi\" &amp; &lt;run&gt;'" in markup
    assert ">a &lt; b &amp; c</text>" in markup


def test_document_wraps_a_single_root() -> None:
    root = Element(tag="svg", attributes=(), children=(), text=None)
    assert document(root) == '<?xml version="1.0" encoding="UTF-8"?>\n<svg/>\n'


def test_shapes_compose_attributes() -> None:
    rounded = rendered(rect(1, 2, 30, 40, fill="#ABCDEF", radius=5))
    assert 'x="1"' in rounded
    assert 'rx="5"' in rounded
    flat = rendered(rect(0, 0, 10, 10, fill="#ABCDEF", radius=None))
    assert "rx" not in flat
    star = rendered(polygon(((0, 0), (1.5, 2)), fill="#112233"))
    assert 'points="0,0 1.5,2"' in star


def test_star_points_form_a_four_pointed_star() -> None:
    points = star_points(50, 50, 10)
    assert len(points) == 8
    assert points[0] == (50, 40)
    assert points[2] == (60, 50)


def test_mixed_hex_blends_linearly() -> None:
    assert mixed_hex("#000000", "#FFFFFF", 0.5) == "#808080"
    assert mixed_hex("#FAF3E1", "#D9A226", 0) == "#FAF3E1"
    assert mixed_hex("#FAF3E1", "#D9A226", 1) == "#D9A226"


def test_letter_slugs_stay_ascii() -> None:
    assert letter_slug("A") == "a"
    assert letter_slug("Ą") == "a-ogonek"
    assert letter_slug("Ż") == "z-dot"
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    for spec in resolved.tiles.letters:
        assert re.fullmatch(r"[a-z0-9-]+", letter_slug(spec.symbol))


def _specimen_markup() -> tuple[str, ThemeTokens]:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    tokens = load_style_tokens(CONFIG_DIR, "default")
    word = SPECIMEN_WORDS[GameName.LITERAKI]
    markup = document(board_specimen(resolved.board, resolved.tiles, tokens.light, word))
    return markup, tokens.light


def test_board_specimen_draws_from_tokens_only() -> None:
    markup, theme = _specimen_markup()
    for letter in "SŁOWA":
        assert f">{letter}</text>" in markup
    assert "×3" in markup
    assert f'fill="{theme.board.star}"' in markup
    assert "stroke" not in markup
    allowed = _token_palette(theme)
    for fill in re.findall(r'fill="(#[0-9A-Fa-f]{6})"', markup):
        assert fill.upper() in allowed


def _token_palette(theme: ThemeTokens) -> set[str]:
    palette = {
        theme.board.surface,
        theme.board.grid,
        theme.board.frame,
        theme.board.star,
        theme.tiles.face,
        theme.tiles.edge,
        theme.tiles.text,
    }
    for premium in list(theme.premiums.values()) + list(theme.category_premiums.values()):
        palette.add(premium.fill)
        palette.add(premium.label)
    for band in theme.tiles.bands.values():
        palette.add(band)
        palette.add(mixed_hex(theme.tiles.face, band, theme.tiles.face_tint))
    return {color.upper() for color in palette}


def test_build_assets_writes_specimens_and_manifest(tmp_path) -> None:
    output = tmp_path / "assets"
    docs = tmp_path / "media"
    records = build_assets(output, docs)
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    listed = {entry["path"] for entry in manifest["assets"]}
    assert {record.path for record in records} == listed
    for path in listed:
        assert (output / path).is_file()
    assert (output / "specimens" / "board-literaki.svg").is_file()
    assert (output / "specimens" / "board-scrabble.svg").is_file()
    assert (docs / "board-literaki.svg").is_file()
