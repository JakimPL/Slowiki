import random

from wordcore.exceptions import IllegalMove, WordcoreError
from wordcore.games.game import Game
from wordcore.moves.action import Exchange, Move, Pass, Play, PlayPlacement
from wordcore.states.state import Phase
from wordcore.tiles.tile import Tile
from wordtable.build import build_rules
from wordtable.catalogue import resolve_scheme
from wordtable.lexicons import load_lexicon
from wordtable.paths import CONFIG_DIR, PROJECT_ROOT


def run(scheme_name: str, players: int) -> None:
    resolved = resolve_scheme(CONFIG_DIR, scheme_name)
    lexicon = load_lexicon(resolved.scheme.dictionary, PROJECT_ROOT / "dictionaries")
    seats = tuple(range(players))
    rules = build_rules(resolved, seats, lexicon)
    game = Game(rules, random.Random())
    while game.position.state.phase != Phase.GAME_OVER:
        _render(game)
        seat = next(iter(game.position.state.to_act))
        print(f"player {seat} to move")
        try:
            command = input("> ").strip()
        except EOFError:
            return
        if command in ("", "quit"):
            return
        try:
            move = _parse_move(game, seat, command)
            game.submit(move, base_seq=game.seq)
        except (WordcoreError, ValueError, IndexError) as error:
            print(f"rejected: {error}")
    _render(game)
    print("game over")


def _parse_move(game: Game, seat: int, command: str) -> Move:
    parts = command.split()
    if not parts:
        raise ValueError("empty command")
    if parts[0] == "pass":
        return Move(player=seat, action=Pass())
    if parts[0] == "exchange":
        return Move(player=seat, action=Exchange(tile_ids=_rack_ids_for(game, seat, parts[1:])))
    if parts[0] == "place":
        word = parts[1]
        row = int(parts[2])
        column = int(parts[3])
        horizontal = parts[4] == "h"
        placements = _placements_for(game, seat, word, row, column, horizontal)
        return Move(player=seat, action=Play(placements=placements))
    raise ValueError(f"unknown command: {parts[0]}")


def _rack_ids_for(game: Game, seat: int, letters: list[str]) -> tuple[int, ...]:
    by_letter: dict[str, list[int]] = {}
    for tile in _rack(game, seat):
        if not tile.blank:
            by_letter.setdefault(tile.letter.lower(), []).append(tile.identifier)
    result: list[int] = []
    for letter in letters:
        key = letter.lower()
        if not by_letter.get(key):
            raise IllegalMove(f"no tile {letter} in rack")
        result.append(by_letter[key].pop(0))
    return tuple(result)


def _placements_for(
    game: Game, seat: int, word: str, row: int, column: int, horizontal: bool
) -> tuple[PlayPlacement, ...]:
    by_letter: dict[str, list[int]] = {}
    blanks: list[int] = []
    for tile in _rack(game, seat):
        if tile.blank:
            blanks.append(tile.identifier)
        else:
            by_letter.setdefault(tile.letter.lower(), []).append(tile.identifier)
    placements: list[PlayPlacement] = []
    for offset, character in enumerate(word):
        target_row = row if horizontal else row + offset
        target_column = column + offset if horizontal else column
        letter = character.lower()
        if by_letter.get(letter):
            placements.append(
                PlayPlacement(
                    tile_id=by_letter[letter].pop(0), row=target_row, column=target_column
                )
            )
        elif blanks:
            placements.append(
                PlayPlacement(
                    tile_id=blanks.pop(0), row=target_row, column=target_column, letter=letter
                )
            )
        else:
            raise IllegalMove(f"no tile for letter {character}")
    return tuple(placements)


def _rack(game: Game, seat: int) -> tuple[Tile, ...]:
    rack = game.position.state.racks[seat]
    return rack if rack is not None else ()


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
