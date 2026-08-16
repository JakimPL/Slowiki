import argparse

from wordtable.play import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wordtable")
    subparsers = parser.add_subparsers(dest="command", required=True)
    play = subparsers.add_parser("play")
    play.add_argument("--scheme", default="literaki")
    play.add_argument("--players", type=int, default=2)
    subparsers.add_parser("serve")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "play":
        run(args.scheme, args.players)
    elif args.command == "serve":
        print("serve arrives in the server phase")


if __name__ == "__main__":
    main()
