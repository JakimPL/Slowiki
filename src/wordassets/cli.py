import argparse
from pathlib import Path

from wordassets.svg import render_board, render_tile
from wordcore.board.preset import board_from_preset
from wordcore.tiles.bag import build_tiles
from wordtable.config import load_board_preset, load_style, load_tile_preset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wordassets")
    subparsers = parser.add_subparsers(dest="command", required=True)
    render = subparsers.add_parser("render")
    render.add_argument("--config", type=Path, default=Path("config"))
    render.add_argument("--style", default="default")
    render.add_argument("--board", default="literaki")
    render.add_argument("--tiles", default="literaki")
    render.add_argument("--output", type=Path, default=Path("assets"))
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command != "render":
        return
    style = load_style(args.config, args.style)
    board = board_from_preset(load_board_preset(args.config, args.board))
    tiles = load_tile_preset(args.config, args.tiles)
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    (output / "board.svg").write_text(render_board(board, style), encoding="utf-8")
    tile_dir = output / "tiles"
    tile_dir.mkdir(parents=True, exist_ok=True)
    written: set[tuple[str, str]] = set()
    for tile in build_tiles(tiles):
        key = (tile.letter, tile.category)
        if key in written:
            continue
        written.add(key)
        name = "blank" if tile.blank else tile.letter
        (tile_dir / f"{name}.svg").write_text(render_tile(tile, style), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
