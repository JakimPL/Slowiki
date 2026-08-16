from wordassets.svg import render_board, render_tile
from wordcore.board.board import Board, Bonus, BonusKind
from wordcore.tiles.tile import Tile
from wordtable.config import StyleConfig


def style() -> StyleConfig:
    return StyleConfig(
        name="test",
        board_color="#2f6f4f",
        text_color="#1a1a1a",
        tile_colors={"red": "#cc4125", "yellow": "#e8c46a"},
        premium_colors={"word_multiplier": "#d9534f", "letter_multiplier": "#5bc0de"},
    )


def test_render_board_contains_cells_and_bonuses() -> None:
    board = Board(
        size=3,
        bonuses=(
            None,
            Bonus(kind=BonusKind.WORD_MULTIPLIER, multiplier=3),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        tiles=(None,) * 9,
    )
    svg = render_board(board, style())
    assert svg.startswith("<svg")
    assert "3W" in svg
    assert "★" in svg
    assert svg.count("<rect") >= 9


def test_render_tile_shows_letter_and_value() -> None:
    tile = Tile(identifier=1, letter="ą", value=5, category="red", blank=False)
    svg = render_tile(tile, style())
    assert "ą" in svg
    assert ">5</text>" in svg


def test_render_blank_tile_shows_star() -> None:
    tile = Tile(identifier=2, letter="", value=0, category="blank", blank=True)
    svg = render_tile(tile, style())
    assert "*" in svg
