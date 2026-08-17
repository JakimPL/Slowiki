import argparse
import logging
from pathlib import Path

from wordassets.build import build_assets

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wordassets")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--output", type=Path, default=Path("assets"))
    build.add_argument("--docs", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    match args.command:
        case "build":
            logging.basicConfig(level=logging.INFO, format="%(message)s")
            records = build_assets(args.output, args.docs)
            logger.info("wrote %d assets under %s", len(records), args.output)


if __name__ == "__main__":
    main()
