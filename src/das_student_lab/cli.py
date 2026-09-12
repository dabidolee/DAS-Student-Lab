"""Small command-line entry point for repository orientation."""

from __future__ import annotations

import argparse

from das_student_lab import __version__
from das_student_lab.datasets import OOI_DATASET


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(prog="das-student-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("info", help="show project status and required data citation")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface."""

    args = build_parser().parse_args(argv)
    if args.command == "info":
        print(f"DAS Student Lab {__version__} (pre-alpha starter)")
        print("Real-data downloading and scientific algorithms are not implemented.")
        print("\nPrimary public dataset citation:")
        print(OOI_DATASET.citation)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
