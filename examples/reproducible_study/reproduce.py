from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from analyze import analyze_archive
from documentation import write_research_documentation

from abmforge.cli.main import main as abmforge_main

STUDY_DIR = Path(__file__).resolve().parent


def reproduce(output: str | Path) -> Path:
    """Run the full reproducible-study workflow and return the archive path."""

    archive_path = Path(output).expanduser()
    if not archive_path.is_absolute():
        archive_path = STUDY_DIR / archive_path

    original_cwd = Path.cwd()
    try:
        os.chdir(STUDY_DIR)
        study_dir_str = str(STUDY_DIR)
        if study_dir_str not in sys.path:
            sys.path.insert(0, study_dir_str)

        abmforge_main(
            [
                "experiment",
                "configs/experiment.yaml",
                "--archive",
                str(archive_path),
                "--overwrite",
            ]
        )
        abmforge_main(["validate", str(archive_path)])
        abmforge_main(["summarize", str(archive_path), "--json"])
        abmforge_main(["report", str(archive_path)])
        analyze_archive(archive_path)
        write_research_documentation(archive_path)
    finally:
        os.chdir(original_cwd)

    return archive_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reproduce the ABMForge threshold-adoption study.")
    parser.add_argument(
        "--output",
        default="outputs/reproducible_study_archive",
        help="Output archive path. Relative paths are resolved inside this example directory.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    archive_path = reproduce(args.output)
    print(f"Reproducible study archive written to: {archive_path}")


if __name__ == "__main__":
    main()
