from typing import Final

from wordcore.board.board import Board, Bonus, BonusKind
from wordcore.tiles.tile import Tile
from wordtable.config import StyleConfig

CELL: Final = 40


def render_board(board: Board, style: StyleConfig) -> str:
    size = board.size
    extent = size * CELL
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{extent}" height="{extent}" '
        f'viewBox="0 0 {extent} {extent}">',
        f'<rect width="{extent}" height="{extent}" fill="{style.board_color}"/>',
    ]
    for row in range(size):
        for column in range(size):
            x = column * CELL
            y = row * CELL
            fill = _bonus_fill(board.bonus_at(row, column), style)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{fill}" '
                f'stroke="#1a1a1a" stroke-width="1"/>'
            )
            bonus = board.bonus_at(row, column)
            label = _bonus_label(bonus)
            if label:
                parts.append(
                    f'<text x="{x + CELL // 2}" y="{y + CELL // 2}" text-anchor="middle" '
                    f'dominant-baseline="middle" font-size="12" fill="{style.text_color}">'
                    f"{label}</text>"
                )
            if row == board.center() and column == board.center():
                parts.append(
                    f'<text x="{x + CELL // 2}" y="{y + CELL // 2}" text-anchor="middle" '
                    f'dominant-baseline="middle" font-size="20" fill="{style.text_color}">★</text>'
                )
    parts.append("</svg>")
    return "".join(parts)


def render_tile(tile: Tile, style: StyleConfig) -> str:
    fill = style.tile_colors.get(tile.category, "#eeeeee")
    letter = tile.letter if tile.letter else "*"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CELL}" height="{CELL}" '
        f'viewBox="0 0 {CELL} {CELL}">',
        f'<rect x="2" y="2" width="{CELL - 4}" height="{CELL - 4}" rx="6" fill="{fill}" '
        f'stroke="#1a1a1a" stroke-width="1"/>',
        f'<text x="{CELL // 2}" y="{CELL // 2 + 2}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="20" fill="{style.text_color}">{letter}</text>',
    ]
    if tile.value:
        parts.append(
            f'<text x="{CELL - 6}" y="{CELL - 6}" text-anchor="end" '
            f'dominant-baseline="middle" font-size="10" fill="{style.text_color}">'
            f"{tile.value}</text>"
        )
    parts.append("</svg>")
    return "".join(parts)


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
