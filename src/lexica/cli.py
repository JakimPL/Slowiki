import argparse
import itertools
from pathlib import Path

from lexica.artifact.envelope import read_header
from lexica.artifact.words import write_word_list
from lexica.dictionaries.sjp import iter_sjp_words


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lexica")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("archive", type=Path)
    header = subparsers.add_parser("header")
    header.add_argument("artifact", type=Path)
    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("archive", type=Path)
    compile_parser.add_argument("output", type=Path)
    fetch_osps = subparsers.add_parser("fetch-osps")
    fetch_osps.add_argument("output", type=Path)
    fetch_english = subparsers.add_parser("fetch-english")
    fetch_english.add_argument("output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    match str(args.command):
        case "inspect":
            words = itertools.islice(iter_sjp_words(args.archive), 10)
            for word in words:
                print(word)

        case "header":
            header = read_header(args.artifact)
            print(
                f"{args.artifact}: {header.kind} format {header.format}, "
                f"{header.entries} entries, {args.artifact.stat().st_size} bytes"
            )

        case "compile":
            write_word_list(iter_sjp_words(args.archive), args.output)
            print(args.output)

        case "fetch-osps":
            print("download the OSPS list from https://www.pfs.org.pl and write it to", args.output)

        case "fetch-english":
            print("download an English word list and write it to", args.output)

        case _:
            raise ValueError(f"unsupported command {args.command}")


if __name__ == "__main__":
    main()
