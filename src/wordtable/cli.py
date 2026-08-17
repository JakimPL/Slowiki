import argparse
import logging

from lexica.names import DictionaryName
from wordtable.lexicons import compile_dictionary
from wordtable.play import run
from wordtable.serve import run as run_server

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wordtable")
    subparsers = parser.add_subparsers(dest="command", required=True)
    play = subparsers.add_parser("play")
    play.add_argument("--scheme", default="literaki")
    play.add_argument("--players", type=int, default=2)
    dictionary = subparsers.add_parser("dictionary")
    dictionary.add_argument("--name", default="sjp")
    subparsers.add_parser("serve")
    return parser


def run_compile(name: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    compiled = compile_dictionary(DictionaryName(name))
    logger.info("compiled lexicon at %s", compiled)


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    match args.command:
        case "play":
            run(args.scheme, args.players)
        case "dictionary":
            run_compile(args.name)
        case "serve":
            run_server()


if __name__ == "__main__":
    main()
