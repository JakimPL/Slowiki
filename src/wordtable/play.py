import random

from wordcore.exceptions import IllegalMove, WordcoreError
from wordcore.games.game import Game
from wordcore.moves.action import Exchange, Pass, Play, PlayPlacement
from wordcore.moves.move import Move
from wordcore.states.state import Phase
from wordcore.tiles.tile import Tile
from wordtable.build import build_rules
from wordtable.catalogue import resolve_scheme
from wordtable.lexicons import load_lexicon
from wordtable.paths import CONFIG_DIR


def run(scheme_name: str, players: int) -> None:
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
    print("game over")  # TODO: logging, not printing


def _handle_command(game: Game) -> bool:
    seat = _current_seat(game)
    print(f"player {seat} to move")
    command = _read_command()  # TODO: logging, not printing
    if command is None:
        return False

    try:
        move = _parse_move(game, seat, command)
        game.submit(move, base_seq=game.seq)

    except (WordcoreError, ValueError, IndexError) as error:
        print(f"rejected: {error}")

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


# TODO: refactor
def _parse_move(game: Game, seat: int, command: str) -> Move:
    parts = command.split()
    if not parts:
        raise ValueError("empty command")

    # TODO: fragile mechanism
    if parts[0] == "pass":
        return Move(player=seat, action=Pass())

    if parts[0] == "exchange":
        return Move(
            player=seat,
            action=Exchange(tile_ids=_rack_ids_for(game, seat, parts[1:])),
        )

    # TODO: refactor - a very fragile mechanism; use NamedTuple
    if parts[0] == "place":
        word = parts[1]
        row = int(parts[2])
        column = int(parts[3])
        horizontal = parts[4] == "h"
        placements = _placements_for(game, seat, word, row, column, horizontal)
        return Move(player=seat, action=Play(placements=placements))

    raise ValueError(f"unknown command: {parts[0]}")


# TODO: refactor
def _rack_ids_for(
    game: Game,
    seat: int,
    letters: list[str],
) -> tuple[int, ...]:
    by_letter: dict[str, list[int]] = {}
    for tile in _rack(game, seat):
        if not tile.blank:
            by_letter.setdefault(tile.letter.upper(), []).append(tile.identifier)

    result: list[int] = []
    for letter in letters:
        key = letter.upper()
        if not by_letter.get(key):
            raise IllegalMove(f"no tile {letter} in rack")

        result.append(by_letter[key].pop(0))

    return tuple(result)


# TODO: refactor
# BTW, at this stage we should NOT use lower/upper at all
# letters should be normalized at this point
def _placements_for(
    game: Game,
    seat: int,
    word: str,
    row: int,
    column: int,
    horizontal: bool,
) -> tuple[PlayPlacement, ...]:
    by_letter: dict[str, list[int]] = {}
    blanks: list[int] = []
    for tile in _rack(game, seat):
        if tile.blank:
            blanks.append(tile.identifier)
        else:
            by_letter.setdefault(tile.letter.upper(), []).append(tile.identifier)

    placements: list[PlayPlacement] = []
    for offset, character in enumerate(word):
        target_row = row if horizontal else row + offset
        target_column = column + offset if horizontal else column
        letter = character.upper()
        if by_letter.get(letter):
            placements.append(
                PlayPlacement(
                    tile_id=by_letter[letter].pop(0),
                    row=target_row,
                    column=target_column,
                )
            )

        elif blanks:
            placements.append(
                PlayPlacement(
                    tile_id=blanks.pop(0),
                    row=target_row,
                    column=target_column,
                    letter=letter,
                )
            )

        else:
            raise IllegalMove(f"no tile for letter {character}")

    return tuple(placements)


def _rack(game: Game, seat: int) -> tuple[Tile, ...]:
    rack = game.position.state.racks[seat]
    return rack if rack is not None else ()


# TODO: refactor
def _render(game: Game) -> None:
    state = game.position.state
    print("scores:", state.scores)
    print("bag:", len(state.bag))
    for seat in game.position.players:
        letters = "".join(tile.letter or "_" for tile in _rack(game, seat))
        print(f"  seat {seat}: {letters}")

    board = game.position.board
    for row in range(board.size):
        cells = []
        for column in range(board.size):
            tile = board.tile_at(row, column)
            if tile is not None:
                cells.append(tile.letter or "_")

            elif board.bonus_at(row, column) is not None:
                cells.append("+")

            else:
                cells.append(".")

        print(" ".join(cells))
