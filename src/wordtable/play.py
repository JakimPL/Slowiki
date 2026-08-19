# TODO: refactor: split into a subpackage
# this module bears too many responsibilities

import logging
import random
from typing import Final, NamedTuple

from wordcore.board.board import Board
from wordcore.errors.exceptions import IllegalMove, WordcoreError
from wordcore.games.game import Game
from wordcore.moves.action import Exchange, Pass, Play, PlayPlacement
from wordcore.moves.move import Move
from wordcore.states.phase import Phase
from wordcore.tiles.tile import Tile
from wordtable.build import build_rules
from wordtable.catalog import resolve_scheme
from wordtable.lexicons import load_lexicon
from wordtable.paths import CONFIG_DIR

logger = logging.getLogger(__name__)

_PLACE_ARGUMENT_COUNT: Final = 4
_ORIENTATIONS: Final = ("h", "v")


class PlaceCommand(NamedTuple):
    word: str
    row: int
    column: int
    horizontal: bool


def run(scheme_name: str, players: int) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    game = _build_game(scheme_name, players)
    _play(game)


def _build_game(scheme_name: str, players: int) -> Game:
    resolved = resolve_scheme(CONFIG_DIR, scheme_name)
    lexicon = load_lexicon(resolved.scheme.dictionary)
    seats = tuple(range(players))
    rules = build_rules(resolved, seats, lexicon)
    return Game(
        rules,
        random.Random(),
        premoves_allowed=resolved.scheme.premoves,
    )


def _play(game: Game) -> None:
    while game.position.state.phase != Phase.GAME_OVER:
        _render(game)
        if not _handle_command(game):
            return

    _render(game)
    logger.info("game over")


def _handle_command(game: Game) -> bool:
    seat = _current_seat(game)
    logger.info("player %d to move", seat)
    command = _read_command()
    if command is None:
        return False

    try:
        move = _parse_move(game, seat, command)
        game.submit(move, base_seq=game.seq)
    except (WordcoreError, ValueError) as error:
        logger.info("rejected: %s", error)

    return True


def _current_seat(game: Game) -> int:
    return next(iter(game.position.state.to_act))


def _read_command() -> str | None:
    try:
        command = input("> ").strip()
    except EOFError:
        return None

    if command in ("", "quit"):
        return None

    return command


def _parse_move(game: Game, seat: int, command: str) -> Move:
    head, *arguments = command.split()
    match head:
        case "pass":
            return Move(player=seat, action=Pass())
        case "exchange":
            return Move(
                player=seat,
                action=Exchange(
                    tile_ids=_rack_ids_for(
                        game,
                        seat,
                        arguments,
                    )
                ),
            )
        case "place":
            return _place_move(game, seat, _parse_place(arguments))
        case _:
            raise ValueError(f"unknown command: {head}")


def _parse_place(arguments: list[str]) -> PlaceCommand:
    if len(arguments) != _PLACE_ARGUMENT_COUNT:
        raise ValueError("place expects: place <word> <row> <column> <h|v>")

    word, row, column, orientation = arguments
    if orientation not in _ORIENTATIONS:
        raise ValueError("orientation must be h or v")

    return PlaceCommand(
        word=word.upper(),
        row=int(row),
        column=int(column),
        horizontal=orientation == "h",
    )


def _place_move(game: Game, seat: int, place: PlaceCommand) -> Move:
    return Move(
        player=seat,
        action=Play(placements=_placements_for(game, seat, place)),
    )


def _rack_ids_for(game: Game, seat: int, letters: list[str]) -> tuple[int, ...]:
    by_letter = _tiles_by_letter(_rack(game, seat))
    result: list[int] = []
    for letter in (entry.upper() for entry in letters):
        pool = by_letter.get(letter)
        if not pool:
            raise IllegalMove(f"no tile {letter} in rack")

        result.append(pool.pop(0))

    return tuple(result)


def _placements_for(
    game: Game,
    seat: int,
    place: PlaceCommand,
) -> tuple[PlayPlacement, ...]:
    rack = _rack(game, seat)
    by_letter = _tiles_by_letter(rack)
    blanks = _blank_ids(rack)
    placements: list[PlayPlacement] = []
    for offset, letter in enumerate(place.word):
        row, column = _target_square(place, offset)
        placements.append(
            _letter_placement(
                by_letter,
                blanks,
                letter,
                row,
                column,
            )
        )

    return tuple(placements)


def _target_square(place: PlaceCommand, offset: int) -> tuple[int, int]:
    if place.horizontal:
        return place.row, place.column + offset

    return place.row + offset, place.column


def _letter_placement(
    by_letter: dict[str, list[int]],
    blanks: list[int],
    letter: str,
    row: int,
    column: int,
) -> PlayPlacement:
    pool = by_letter.get(letter)
    if pool:
        return PlayPlacement(tile_id=pool.pop(0), row=row, column=column)

    if blanks:
        return PlayPlacement(
            tile_id=blanks.pop(0),
            row=row,
            column=column,
            letter=letter,
        )

    raise IllegalMove(f"no tile for letter {letter}")


def _tiles_by_letter(rack: tuple[Tile, ...]) -> dict[str, list[int]]:
    by_letter: dict[str, list[int]] = {}
    for tile in rack:
        if not tile.blank:
            by_letter.setdefault(tile.letter, []).append(tile.identifier)

    return by_letter


def _blank_ids(rack: tuple[Tile, ...]) -> list[int]:
    return [tile.identifier for tile in rack if tile.blank]


def _rack(game: Game, seat: int) -> tuple[Tile, ...]:
    rack = game.position.state.racks[seat]
    return rack if rack is not None else ()


def _render(game: Game) -> None:
    _render_scores(game)
    _render_racks(game)
    _render_board(game)


def _render_scores(game: Game) -> None:
    state = game.position.state
    logger.info("scores: %s", state.scores)
    logger.info("bag: %d tiles", len(state.bag))


def _render_racks(game: Game) -> None:
    for seat in game.position.players:
        letters = "".join(tile.letter or "_" for tile in _rack(game, seat))
        logger.info("  seat %d: %s", seat, letters)


def _render_board(game: Game) -> None:
    board = game.position.board
    for row in range(board.size):
        logger.info(" ".join(_cell_glyph(board, row, column) for column in range(board.size)))


def _cell_glyph(board: Board, row: int, column: int) -> str:
    tile = board.tile_at(row, column)
    if tile is not None:
        return tile.letter or "_"

    if board.bonus_at(row, column) is not None:
        return "+"

    return "."
