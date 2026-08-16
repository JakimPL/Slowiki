import argparse
import itertools
from pathlib import Path

from lexica.compile import compile_lexicon
from lexica.sjp import iter_sjp_words


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lexica")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("archive", type=Path)
    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("archive", type=Path)
    compile_parser.add_argument("output", type=Path)
    fetch_osps = subparsers.add_parser("fetch-osps")
    fetch_osps.add_argument("output", type=Path)
    fetch_english = subparsers.add_parser("fetch-english")
    fetch_english.add_argument("output", type=Path)
    subparsers.add_parser("label")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "inspect":
        words = itertools.islice(iter_sjp_words(args.archive), 10)
        for word in words:
            print(word)
    elif args.command == "compile":
        compile_lexicon(iter_sjp_words(args.archive), args.output)
        print(args.output)
    elif args.command == "fetch-osps":
        print("download the OSPS list from https://www.pfs.org.pl and write it to", args.output)
    elif args.command == "fetch-english":
        print("download an English word list and write it to", args.output)
    elif args.command == "label":
        print("the LLM labelling pipeline lands here")
