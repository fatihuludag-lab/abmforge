from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import abmforge
from abmforge.experiment.archive import ExperimentArchive
from abmforge.experiment.result import RunResult
from abmforge.experiment.scenario import Scenario

_REPOSITORY_URL = "https://github.com/fatihuludag-lab/abmforge"
_TITLE = "ABMForge: Reproducible Agent-Based Modelling in Python"
_AUTHOR = "Fatih Uludağ"
_LICENSE = "Apache-2.0"


def format_citation(citation_format: str = "text") -> str:
    """Return citation information for ABMForge."""
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
            "or published computational experiments, please cite the software.\n"
            "A machine-readable citation is available in CITATION.cff."
        )

    raise ValueError(f"Unsupported citation format: {citation_format}")


def _write_run_summary(result: RunResult, archive: ExperimentArchive) -> Path:
    """Write a compact machine-readable run summary into the archive."""
    summary = {
        "run_id": result.run_id,
        "status": result.status,
        "steps": result.steps,
        "stop_reason": result.stop_reason,
        "error": result.error,
        "exception_type": result.exception_type,
    }
    path = archive.reports_dir / "run_summary.json"
    path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return path


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

    run_parser = subparsers.add_parser(
        "run",
        help="Run a scenario YAML file and write an experiment archive",
    )
    run_parser.add_argument(
        "scenario",
        help="Path to a scenario YAML file",
    )
    run_parser.add_argument(
        "--archive",
        required=True,
        help="Output directory for the ABMForge experiment archive",
    )
    run_parser.add_argument(
        "--format",
        choices=["json", "parquet"],
        default="json",
        help="Archive data format",
    )
    run_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the archive directory if it already exists",
    )
    run_parser.add_argument(
        "--allow-failed",
        action="store_true",
        help="Exit with status 0 even if the model run fails",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate an experiment archive",
    )
    validate_parser.add_argument("path", help="Path to an ABMForge experiment archive")

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

    if args.command == "run":
        scenario_path = Path(args.scenario).resolve()

        for import_path in (Path.cwd().resolve(), scenario_path.parent):
            import_path_str = str(import_path)
            if import_path_str not in sys.path:
                sys.path.insert(0, import_path_str)

        scenario = Scenario.from_yaml(scenario_path)
        result = scenario.run(raise_on_error=False)

        archive = ExperimentArchive.create(args.archive, overwrite=args.overwrite)
        archive.write_run_outputs(result.dataset, format=args.format)
        summary_path = _write_run_summary(result, archive)

        print(f"Run completed: {result.run_id}")
        print(f"Status: {result.status}")
        print(f"Steps: {result.steps}")
        print(f"Archive written: {archive.path}")
        print(f"Summary written: {summary_path}")

        if result.status == "failed" and not args.allow_failed:
            raise SystemExit(1)

        return

    if args.command == "validate":
        archive = ExperimentArchive(Path(args.path))
        errors = archive.validate()

        if errors:
            print("Archive validation failed:")
            for error in errors:
                print(f"- {error}")
            raise SystemExit(1)

        print("Archive validation passed")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
