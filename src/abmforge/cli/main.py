from __future__ import annotations

import argparse
from collections.abc import Sequence

import abmforge


_REPOSITORY_URL = "https://github.com/fatihuludag-lab/abmforge"
_TITLE = "ABMForge: Reproducible Agent-Based Modelling in Python"
_AUTHOR = "Fatih Uludağ"
_LICENSE = "Apache-2.0"


def format_citation(citation_format: str = "text") -> str:
    """Return citation information for ABMForge.

    Parameters
    ----------
    citation_format:
        Citation output format. Supported values are ``"text"`` and ``"bibtex"``.
    """
    if citation_format == "bibtex":
        return (
            "@software{uludag_abmforge_2026,\n"
            f"  author = {{{_AUTHOR}}},\n"
            f"  title = {{{_TITLE}}},\n"
            "  year = {2026},\n"
            f"  version = {{{abmforge.__version__}}},\n"
            f"  url = {{{_REPOSITORY_URL}}},\n"
            f"  license = {{{_LICENSE}}}\n"
            "}"
        )

    if citation_format == "text":
        return (
            f"{_TITLE}\n"
            f"Author: {_AUTHOR}\n"
            f"Version: {abmforge.__version__}\n"
            f"Repository: {_REPOSITORY_URL}\n"
            f"License: {_LICENSE}\n\n"
            "If you use ABMForge in research, teaching, policy modelling, "
            "or published computational experiments, please cite the software. "
            "A machine-readable citation is available in CITATION.cff."
        )

    raise ValueError(f"Unsupported citation format: {citation_format}")


def build_parser() -> argparse.ArgumentParser:
    """Build the ABMForge command-line parser."""
    parser = argparse.ArgumentParser(prog="abmforge")
    parser.add_argument("--version", action="store_true", help="Show package version")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("info", help="Show package information")

    cite_parser = subparsers.add_parser("cite", help="Show citation information")
    cite_parser.add_argument(
        "--format",
        choices=["text", "bibtex"],
        default="text",
        help="Citation output format",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Run the ABMForge command-line interface."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(abmforge.__version__)
        return

    if args.command == "info":
        print(f"ABMForge {abmforge.__version__}")
        print("Core objects: Model, Agent, AgentCollection, GridWorld, Scenario")
        print(f"Repository: {_REPOSITORY_URL}")
        return

    if args.command == "cite":
        print(format_citation(args.format))
        return

    parser.print_help()


if __name__ == "__main__":
    main()