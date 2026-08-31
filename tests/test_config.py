import pytest
from pydantic import ValidationError

from lexica.artifact.kind import ArtifactKind
from lexica.names import DictionaryName
from wordcore.board.preset import board_from_preset
from wordtable import paths
from wordtable.catalog import list_schemes, offerings, resolve_scheme
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


def test_catalog_offers_every_scheme() -> None:
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
    paths.dictionary_compiled(DictionaryName.ENGLISH, ArtifactKind.WORDS).touch()
    assert dictionary_ready(DictionaryName.ENGLISH) is True


def test_resolve_scheme_builds_board() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    board = board_from_preset(resolved.board)
    assert board.size == 15


def test_literaki_tile_counts() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    total = sum(letter.count for letter in resolved.tiles.letters) + resolved.tiles.blanks
    assert total == 100
    assert resolved.scheme.rack_size == 7


def test_the_solo_scheme_deals_the_whole_bag() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "solo-literaki")
    assert resolved.scheme.rack_size is None
    assert resolved.tiles == resolve_scheme(CONFIG_DIR, "literaki").tiles


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


def test_default_palette_separates_the_success_accent() -> None:
    tokens = load_style_tokens(CONFIG_DIR, "default")
    for theme in (tokens.light, tokens.dark):
        accents = theme.accents
        assert accents.success not in {accents.primary, accents.danger, accents.premove}
        assert accents.success not in set(theme.tiles.bands.values())


def test_default_palette_covers_literaki_categories() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    categories = {letter.category for letter in resolved.tiles.letters}
    tokens = load_style_tokens(CONFIG_DIR, "default")
    for theme in (tokens.light, tokens.dark):
        assert categories <= set(theme.tiles.bands)
        assert categories <= set(theme.category_premiums)
