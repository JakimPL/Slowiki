import argparse
import logging
from pathlib import Path

from lexica.names import DictionaryName
from wordtable.coverage import report_coverage, summary_of
from wordtable.lexicons import compile_dictionary
from wordtable.paths import POLIMORF_TABLE, dictionary_coverage, dictionary_unread
from wordtable.play import run
from wordtable.rescue import compile_rescue
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
    rescue = subparsers.add_parser("rescue")
    rescue.add_argument("--name", default="sjp")
    rescue.add_argument("--polimorf", type=Path, default=POLIMORF_TABLE)
    coverage = subparsers.add_parser("coverage")
    coverage.add_argument("--name", default="sjp")
    serve = subparsers.add_parser("serve")
    serve.add_argument("--host")
    serve.add_argument("--port", type=int)
    return parser


def run_compile(name: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    compiled = compile_dictionary(DictionaryName(name))
    logger.info("compiled lexicon at %s", compiled)


def run_rescue(name: str, polimorf: Path) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    compiled = compile_rescue(DictionaryName(name), polimorf)
    logger.info("compiled rescue table at %s", compiled)


def run_coverage(name: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    result = report_coverage(DictionaryName(name))
    logger.info(summary_of(result.coverage))
    logger.info("wrote %s", dictionary_coverage(DictionaryName(name)))
    logger.info("wrote %s", dictionary_unread(DictionaryName(name)))


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    match args.command:
        case "play":
            run(args.scheme, args.players)

        case "dictionary":
            run_compile(args.name)

        case "rescue":
            run_rescue(args.name, args.polimorf)

        case "coverage":
            run_coverage(args.name)

        case "serve":
            run_server(args.host, args.port)


if __name__ == "__main__":
    main()
