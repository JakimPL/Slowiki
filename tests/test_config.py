from pathlib import Path

import pytest
from pydantic import ValidationError

from lexica.names import DictionaryName
from wordcore.board.preset import board_from_preset
from wordtable import paths
from wordtable.catalogue import list_schemes, offerings, resolve_scheme
from wordtable.config import StyleTokens, load_style_tokens, read_config
from wordtable.lexicons import dictionary_ready
from wordtable.paths import CONFIG_DIR


def test_config_tree_exists() -> None:
    assert (CONFIG_DIR / "config.yaml").is_file()


def test_read_config() -> None:
    configuration = read_config(CONFIG_DIR / "config.yaml")
    assert 0 < configuration.service.port < 65536
    assert configuration.scheme in set(list_schemes(CONFIG_DIR))


def test_schemes_are_listed() -> None:
    schemes = list_schemes(CONFIG_DIR)
    assert {"literaki", "scrabble", "solo-literaki"} <= set(schemes)


def test_catalogue_offers_every_scheme() -> None:
    by_name = {offering.name: offering for offering in offerings(CONFIG_DIR)}
    assert {"literaki", "scrabble", "solo-literaki"} <= set(by_name)
    assert by_name["scrabble"].dictionary == DictionaryName.ENGLISH
    assert by_name["literaki"].dictionary == DictionaryName.SJP


def test_dictionary_readiness_follows_files(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(paths, "DICTIONARIES_DIR", tmp_path)
    assert dictionary_ready(DictionaryName.ENGLISH) is False
    (tmp_path / "english.zip").touch()
    assert dictionary_ready(DictionaryName.ENGLISH) is True
    (tmp_path / "english.zip").unlink()
    (tmp_path / f"english.v{paths.LEXICON_FORMAT}.lexicon").touch()
    assert dictionary_ready(DictionaryName.ENGLISH) is True


def test_resolve_scheme_builds_board() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    board = board_from_preset(resolved.board)
    assert board.size == 15


def test_scheme_allowed_pos_accepts_known_and_rejects_unknown(tmp_path: Path) -> None:
    from wordtable.config import load_scheme

    body = """\
game: literaki
board: literaki
tiles: literaki
dictionary: sjp
min_players: 2
max_players: 8
validate_on_play: true
premoves: true
exchange_limit: 3
exchange_min_bag: 7
pass_allowed: true
time:
  per_turn_seconds: null
  increment_seconds: 0
  total_seconds: null
pass_end_limit: 2
scoreless_end_limit: null
bingo_bonus: 50
allowed_pos: [rzeczownik, czasownik]
base_form_only: true
"""
    schemes_dir = tmp_path / "schemes"
    schemes_dir.mkdir()
    path = schemes_dir / "filtered.yaml"
    path.write_text(body, encoding="utf-8")
    scheme = load_scheme(tmp_path, "filtered")
    assert scheme.allowed_pos == ("rzeczownik", "czasownik")
    assert scheme.base_form_only is True

    path.write_text(
        body.replace(
            "allowed_pos: [rzeczownik, czasownik]",
            "allowed_pos: [nieistnieje]",
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_scheme(tmp_path, "filtered")


def test_literaki_tile_counts() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    total = sum(letter.count for letter in resolved.tiles.letters) + resolved.tiles.blanks
    assert total == 100
    assert resolved.tiles.rack_size == 7


def test_solo_tile_preset_is_unlimited() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "solo-literaki")
    assert resolved.tiles.rack_size is None


def test_style_tokens_load() -> None:
    tokens = load_style_tokens(CONFIG_DIR, "default")
    assert tokens.name == "default"
    assert tokens.font_family == "Lato"
    assert {"word_2", "word_3", "letter_2", "letter_3"} <= set(tokens.light.premiums)


def test_style_tokens_reject_invalid_hex() -> None:
    payload = load_style_tokens(CONFIG_DIR, "default").model_dump()
    payload["light"]["board"]["surface"] = "linen"
    with pytest.raises(ValidationError):
        StyleTokens.model_validate(payload)


def test_tile_faces_carry_a_bounded_category_tint() -> None:
    tokens = load_style_tokens(CONFIG_DIR, "default")
    for theme in (tokens.light, tokens.dark):
        assert 0 < theme.tiles.face_tint < 1
    payload = tokens.model_dump()
    payload["light"]["tiles"]["face_tint"] = 1.5
    with pytest.raises(ValidationError):
        StyleTokens.model_validate(payload)


def test_default_palette_keeps_premiums_apart() -> None:
    tokens = load_style_tokens(CONFIG_DIR, "default")
    for theme in (tokens.light, tokens.dark):
        red = theme.category_premiums["red"].fill
        assert theme.premiums["word_2"].fill != red
        assert theme.premiums["word_3"].fill != red
        assert theme.board.surface not in set(theme.tiles.bands.values())


def test_default_palette_covers_literaki_categories() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    categories = {letter.category for letter in resolved.tiles.letters}
    tokens = load_style_tokens(CONFIG_DIR, "default")
    for theme in (tokens.light, tokens.dark):
        assert categories <= set(theme.tiles.bands)
        assert categories <= set(theme.category_premiums)
