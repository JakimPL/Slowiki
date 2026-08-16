from wordcore.board.preset import board_from_preset
from wordtable.catalogue import list_schemes, resolve_scheme
from wordtable.config import load_style, read_config
from wordtable.paths import CONFIG_DIR


def test_config_tree_exists() -> None:
    assert (CONFIG_DIR / "config.yaml").is_file()


def test_read_config() -> None:
    configuration = read_config(CONFIG_DIR / "config.yaml")
    assert configuration.service.port == 8000
    assert configuration.scheme == "literaki"


def test_schemes_are_listed() -> None:
    schemes = list_schemes(CONFIG_DIR)
    assert {"literaki", "scrabble", "solo-literaki"} <= set(schemes)


def test_resolve_scheme_builds_board() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    board = board_from_preset(resolved.board)
    assert board.size == 15


def test_literaki_tile_counts() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    total = sum(letter.count for letter in resolved.tiles.letters) + resolved.tiles.blanks
    assert total == 100
    assert resolved.tiles.rack_size == 7


def test_solo_tile_preset_is_unlimited() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "solo-literaki")
    assert resolved.tiles.rack_size is None


def test_style_loads() -> None:
    style = load_style(CONFIG_DIR, "default")
    assert style.board_color.startswith("#")
    assert "yellow" in style.tile_colors
