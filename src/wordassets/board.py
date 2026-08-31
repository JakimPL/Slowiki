from typing import Final

from wordassets.colors import mixed_hex
from wordassets.drawing.node import Element
from wordassets.drawing.shapes import glyph, polygon, rect, svg
from wordassets.geometry import star_points
from wordassets.tiles import tile_group
from wordcore.board.board import Board
from wordcore.board.bonus import Bonus, BonusKind
from wordcore.board.preset import BoardPreset, board_from_preset
from wordcore.tiles.tile import LetterSpec
from wordcore.tiles.tileset import TileSet
from wordgames.names import GameName
from wordtable.config import PremiumTokens, ThemeTokens

SPECIMEN_WORDS: Final[dict[GameName, str]] = {
    GameName.LITERAKI: "SŁOWIKI",
    GameName.SCRABBLE: "WORDS",
}

_CELL: Final = 40.0
_GAP: Final = 1.0
_FRAME: Final = 8.0
_LABEL_SIZE_RATIO: Final = 0.34
_LABEL_WEIGHT: Final = 600
_STAR_RADIUS_RATIO: Final = 0.3
_LABEL_DROP_RATIO: Final = 0.5


def board_specimen(
    preset: BoardPreset,
    tiles: TileSet,
    theme: ThemeTokens,
    word: str,
) -> Element:
    board = board_from_preset(preset)
    span = board.size * _CELL + (board.size + 1) * _GAP + 2 * _FRAME
    children: list[Element] = [
        rect(0, 0, span, span, fill=theme.board.frame, radius=_FRAME),
        rect(
            _FRAME,
            _FRAME,
            span - 2 * _FRAME,
            span - 2 * _FRAME,
            fill=theme.board.grid,
            radius=_FRAME / 2,
        ),
    ]
    for index in range(board.size * board.size):
        children.extend(_cell_shapes(board, index, theme))

    children.append(_center_star(board, theme))
    children.extend(_word_tiles(board, tiles, theme, word))
    return svg(span, span, tuple(children))


def _cell_origin(board: Board, index: int) -> tuple[float, float]:
    row, column = divmod(index, board.size)
    x = _FRAME + _GAP + column * (_CELL + _GAP)
    y = _FRAME + _GAP + row * (_CELL + _GAP)
    return x, y


def _cell_shapes(
    board: Board,
    index: int,
    theme: ThemeTokens,
) -> list[Element]:
    x, y = _cell_origin(board, index)
    bonus = board.bonuses[index]
    if bonus is None:
        return [
            rect(
                x,
                y,
                _CELL,
                _CELL,
                fill=theme.board.surface,
                radius=None,
            )
        ]

    tokens = _premium_tokens(bonus, theme)
    shapes = [rect(x, y, _CELL, _CELL, fill=tokens.fill, radius=None)]
    if index != _center_index(board):
        shapes.append(
            glyph(
                x + _CELL / 2,
                y + _CELL * _LABEL_DROP_RATIO,
                _premium_label(bonus),
                fill=_glyph_color(tokens, theme),
                size=_CELL * _LABEL_SIZE_RATIO,
                weight=_LABEL_WEIGHT,
                anchor="middle",
            )
        )
    return shapes


def _premium_tokens(bonus: Bonus, theme: ThemeTokens) -> PremiumTokens:
    if bonus.kind == BonusKind.CATEGORY_MULTIPLIER:
        return theme.category_premiums[bonus.category or ""]

    family = "word" if bonus.kind == BonusKind.WORD_MULTIPLIER else "letter"
    return theme.premiums[f"{family}_{bonus.multiplier}"]


def _glyph_color(tokens: PremiumTokens, theme: ThemeTokens) -> str:
    return mixed_hex(tokens.fill, tokens.label, theme.board.premium_label_share)


def _premium_label(bonus: Bonus) -> str:
    if bonus.kind == BonusKind.WORD_MULTIPLIER:
        return f"{bonus.multiplier}×"

    return f"×{bonus.multiplier}"


def _center_index(board: Board) -> int:
    middle = board.size // 2
    return middle * board.size + middle


def _center_star(board: Board, theme: ThemeTokens) -> Element:
    x, y = _cell_origin(board, _center_index(board))
    return polygon(
        star_points(x + _CELL / 2, y + _CELL / 2, _CELL * _STAR_RADIUS_RATIO),
        fill=theme.board.star,
    )


def _word_tiles(
    board: Board,
    tiles: TileSet,
    theme: ThemeTokens,
    word: str,
) -> list[Element]:
    by_symbol = {spec.symbol: spec for spec in tiles.letters}
    middle = board.size // 2
    start = middle - len(word) // 2
    shapes: list[Element] = []
    for offset, symbol in enumerate(word):
        spec = _letter_spec(by_symbol, symbol)
        x, y = _cell_origin(board, middle * board.size + start + offset)
        shapes.append(
            tile_group(
                x,
                y,
                _CELL,
                spec.symbol,
                spec.value,
                spec.category,
                theme,
            )
        )

    return shapes


def _letter_spec(by_symbol: dict[str, LetterSpec], symbol: str) -> LetterSpec:
    spec = by_symbol.get(symbol)
    if spec is None:
        raise KeyError(f"specimen letter '{symbol}' is missing from the tile set")

    return spec
