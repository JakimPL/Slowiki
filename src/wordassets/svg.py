from pathlib import Path
from string import Template
from typing import Final

from wordcore.board.board import Board, Bonus, BonusKind
from wordcore.tiles.tile import Tile
from wordtable.config import StyleConfig

CELL: Final = 40
_TEMPLATES_DIR: Final = Path(__file__).resolve().parent / "templates"
_BOARD_TEMPLATE = Template((_TEMPLATES_DIR / "board.svg").read_text(encoding="utf-8"))
_CELL_TEMPLATE = Template((_TEMPLATES_DIR / "cell.svg").read_text(encoding="utf-8"))
_TILE_TEMPLATE = Template((_TEMPLATES_DIR / "tile.svg").read_text(encoding="utf-8"))


def render_board(board: Board, style: StyleConfig) -> str:
    extent = board.size * CELL
    cells = "".join(
        _render_cell(board, style, row, column)
        for row in range(board.size)
        for column in range(board.size)
    )
    return _BOARD_TEMPLATE.substitute(extent=extent, board_color=style.board_color, cells=cells)


def render_tile(tile: Tile, style: StyleConfig) -> str:
    fill = style.tile_colors.get(tile.category, "#eeeeee")
    letter = tile.letter or "*"
    value_text = (
        f'<text x="{CELL - 6}" y="{CELL - 6}" text-anchor="end" '
        f'dominant-baseline="middle" font-size="10" fill="{style.text_color}">{tile.value}</text>'
        if tile.value
        else ""
    )
    return _TILE_TEMPLATE.substitute(
        cell=CELL,
        inner=CELL - 4,
        center=CELL // 2,
        center_plus=CELL // 2 + 2,
        fill=fill,
        text_color=style.text_color,
        letter=letter,
        value_text=value_text,
    )


def _render_cell(board: Board, style: StyleConfig, row: int, column: int) -> str:
    x = column * CELL
    y = row * CELL
    fill = _bonus_fill(board.bonus_at(row, column), style)
    is_center = row == board.center() and column == board.center()
    text = _cell_text(board.bonus_at(row, column), style, x, y, is_center)
    return _CELL_TEMPLATE.substitute(cell=CELL, x=x, y=y, fill=fill, text=text)


def _cell_text(bonus: Bonus | None, style: StyleConfig, x: int, y: int, is_center: bool) -> str:
    label = "★" if is_center else _bonus_label(bonus)
    if not label:
        return ""
    return (
        f'<text x="{x + CELL // 2}" y="{y + CELL // 2}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="20" fill="{style.text_color}">{label}</text>'
    )


def _bonus_fill(bonus: Bonus | None, style: StyleConfig) -> str:
    if bonus is None:
        return style.board_color
    match bonus.kind:
        case BonusKind.CATEGORY_MULTIPLIER:
            return style.tile_colors.get(bonus.category or "", style.board_color)
        case BonusKind.WORD_MULTIPLIER:
            return style.premium_colors.get(BonusKind.WORD_MULTIPLIER.value, style.board_color)
        case BonusKind.LETTER_MULTIPLIER:
            return style.premium_colors.get(BonusKind.LETTER_MULTIPLIER.value, style.board_color)


def _bonus_label(bonus: Bonus | None) -> str:
    if bonus is None:
        return ""
    match bonus.kind:
        case BonusKind.WORD_MULTIPLIER:
            return f"{bonus.multiplier}W"
        case BonusKind.LETTER_MULTIPLIER:
            return f"{bonus.multiplier}L"
        case _:
            return ""
