import json
import random
from pathlib import Path
from typing import Any, Final

from tests.scoring.authored import authored_score

from wordcore.board.board import Board
from wordcore.board.bonus import Bonus, BonusKind
from wordcore.errors.exceptions import IllegalMove
from wordcore.rules.words.formed import formed_words, validate_anchor
from wordcore.rules.words.placement import Placement, board_with_placements
from wordcore.tiles.tile import Tile

OUTPUT: Final[Path] = (
    Path(__file__).resolve().parents[1] / "frontend" / "tests" / "parity" / "scoring.json"
)

_SEED: Final = 20260817
_SIZE: Final = 15
_CASES: Final = 16
_BONUS_CHANCE: Final = 0.16
_ATTEMPTS: Final = 400
_INDENT: Final = 2
_LETTERS: Final = "AĄBCĆDEĘKLŁNOÓRSTWZŻ"
_CATEGORIES: Final = ("yellow", "green", "blue", "red")
_MAX_VALUE: Final = 5
_MAX_PLACED: Final = 4
_OPENING_MAX: Final = 5
_BLANK_CHANCE: Final = 0.1

_BONUS_CHOICES: Final = (
    Bonus(kind=BonusKind.WORD_MULTIPLIER, multiplier=2),
    Bonus(kind=BonusKind.WORD_MULTIPLIER, multiplier=3),
    Bonus(kind=BonusKind.LETTER_MULTIPLIER, multiplier=2),
    Bonus(kind=BonusKind.LETTER_MULTIPLIER, multiplier=3),
    Bonus(kind=BonusKind.CATEGORY_MULTIPLIER, multiplier=3, category="red"),
    Bonus(kind=BonusKind.CATEGORY_MULTIPLIER, multiplier=2, category="yellow"),
    Bonus(kind=BonusKind.CATEGORY_MULTIPLIER, multiplier=3, category="blue"),
    Bonus(kind=BonusKind.CATEGORY_MULTIPLIER, multiplier=2, category="green"),
)


class _TileMint:
    def __init__(self, rng: random.Random) -> None:
        self._rng = rng
        self._next_identifier = 0

    def tile(self) -> Tile:
        self._next_identifier += 1
        if self._rng.random() < _BLANK_CHANCE:
            return Tile(
                identifier=self._next_identifier,
                letter=self._rng.choice(_LETTERS),
                value=0,
                category="blank",
                blank=True,
            )
        return Tile(
            identifier=self._next_identifier,
            letter=self._rng.choice(_LETTERS),
            value=self._rng.randint(1, _MAX_VALUE),
            category=self._rng.choice(_CATEGORIES),
            blank=False,
        )


def main(output: Path) -> None:
    rng = random.Random(_SEED)
    mint = _TileMint(rng)
    board = _empty_board(rng)
    cases: list[dict[str, Any]] = []
    board = _committed(board, _opening_placements(rng, mint, board, cases))
    while len(cases) < _CASES:
        board = _committed(board, _legal_placements(rng, mint, board, cases))

    body = json.dumps({"cases": cases}, indent=_INDENT, ensure_ascii=False, sort_keys=True) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(body, encoding="utf-8")
    print(f"{output}: {len(cases)} cases")


def _empty_board(rng: random.Random) -> Board:
    bonuses = tuple(
        rng.choice(_BONUS_CHOICES) if rng.random() < _BONUS_CHANCE else None
        for _ in range(_SIZE * _SIZE)
    )
    return Board(size=_SIZE, bonuses=bonuses, tiles=(None,) * (_SIZE * _SIZE))


def _opening_placements(
    rng: random.Random,
    mint: _TileMint,
    board: Board,
    cases: list[dict[str, Any]],
) -> tuple[Placement, ...]:
    center = _SIZE // 2
    length = rng.randint(2, _OPENING_MAX)
    start = rng.randint(center - length + 1, center)
    placements = tuple(
        Placement(tile=mint.tile(), row=center, column=start + offset) for offset in range(length)
    )
    _record_case(board, placements, cases)
    return placements


def _legal_placements(
    rng: random.Random,
    mint: _TileMint,
    board: Board,
    cases: list[dict[str, Any]],
) -> tuple[Placement, ...]:
    for _ in range(_ATTEMPTS):
        placements = _proposed(rng, mint, board)
        try:
            validate_anchor(board, placements)
            formed_words(board, placements)
        except IllegalMove:
            continue

        _record_case(board, placements, cases)
        return placements

    raise RuntimeError("no legal placement found")


def _proposed(
    rng: random.Random,
    mint: _TileMint,
    board: Board,
) -> tuple[Placement, ...]:
    count = rng.randint(1, _MAX_PLACED)
    horizontal = rng.random() < 0.5
    row = rng.randrange(_SIZE)
    column = rng.randrange(_SIZE)
    placements: list[Placement] = []
    while len(placements) < count and board.in_bounds(row, column):
        if board.tile_at(row, column) is None:
            placements.append(
                Placement(
                    tile=mint.tile(),
                    row=row,
                    column=column,
                )
            )
        if horizontal:
            column += 1
        else:
            row += 1

    return tuple(placements)


def _record_case(
    board: Board,
    placements: tuple[Placement, ...],
    cases: list[dict[str, Any]],
) -> None:
    words, total = authored_score(board, placements)
    cases.append(
        {
            "name": f"case-{len(cases) + 1}",
            "size": board.size,
            "bonuses": _sparse_bonuses(board),
            "tiles": _sparse_tiles(board),
            "placements": [
                {
                    "index": board.index(placement.row, placement.column),
                    **_tile_json(placement.tile),
                }
                for placement in placements
            ],
            "words": [[text, points] for text, points in words],
            "total": total,
        }
    )


def _sparse_bonuses(board: Board) -> list[dict[str, Any]]:
    return [
        {
            "index": index,
            "kind": bonus.kind.value,
            "multiplier": bonus.multiplier,
            "category": bonus.category,
        }
        for index, bonus in enumerate(board.bonuses)
        if bonus is not None
    ]


def _sparse_tiles(board: Board) -> list[dict[str, Any]]:
    return [
        {"index": index, **_tile_json(tile)}
        for index, tile in enumerate(board.tiles)
        if tile is not None
    ]


def _tile_json(tile: Tile) -> dict[str, Any]:
    return {
        "identifier": tile.identifier,
        "letter": tile.letter,
        "value": tile.value,
        "category": tile.category,
        "blank": tile.blank,
    }


def _committed(board: Board, placements: tuple[Placement, ...]) -> Board:
    return board_with_placements(board, placements)


if __name__ == "__main__":
    main(OUTPUT)
