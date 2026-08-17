import argparse
import itertools
import json
from pathlib import Path

from lexica.compile import compile_lexicon, compile_morph_lexicon
from lexica.dictionaries.sjp import iter_sjp_words
from lexica.morph.index import analyse_dictionary
from lexica.morph.report import build_report
from lexica.morph.sources.sgjp import build_morfeusz_analyzer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lexica")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("archive", type=Path)
    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("archive", type=Path)
    compile_parser.add_argument("output", type=Path)
    compile_parser.add_argument("--polimorf", type=Path, default=None)
    compile_text_parser = subparsers.add_parser("compile-text")
    compile_text_parser.add_argument("archive", type=Path)
    compile_text_parser.add_argument("output", type=Path)
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("archive", type=Path)
    analyze_parser.add_argument("--polimorf", type=Path, default=None)
    analyze_parser.add_argument("--limit", type=int, default=None)
    fetch_osps = subparsers.add_parser("fetch-osps")
    fetch_osps.add_argument("output", type=Path)
    fetch_english = subparsers.add_parser("fetch-english")
    fetch_english.add_argument("output", type=Path)
    subparsers.add_parser("label")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    match str(args.command):
        case "inspect":
            words = itertools.islice(iter_sjp_words(args.archive), 10)
            for word in words:
                print(word)

        case "compile":
            compile_morph_lexicon(
                tuple(iter_sjp_words(args.archive)),
                build_morfeusz_analyzer(),
                args.polimorf,
                args.output,
            )
            print(args.output)

        case "compile-text":
            compile_lexicon(iter_sjp_words(args.archive), args.output)
            print(args.output)

        case "analyze":
            _run_analyze(args)

        case "fetch-osps":
            print("download the OSPS list from https://www.pfs.org.pl and write it to", args.output)

        case "fetch-english":
            print("download an English word list and write it to", args.output)

        case "label":
            print("the LLM labelling pipeline lands here")

        case _:
            raise ValueError(f"unsupported command {args.command}")


def _run_analyze(args: argparse.Namespace) -> None:
    words = tuple(iter_sjp_words(args.archive))
    if args.limit is not None:
        words = words[: args.limit]
    analyzer = build_morfeusz_analyzer()
    result = analyse_dictionary(words, analyzer, args.polimorf)
    print(json.dumps(build_report(result).model_dump(), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
