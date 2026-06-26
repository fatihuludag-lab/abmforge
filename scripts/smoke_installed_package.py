from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import distribution, version
from pathlib import Path


def run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run a command and fail with a useful message if it exits non-zero."""

    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        message = [
            f"Command failed with exit code {result.returncode}: {' '.join(command)}",
            "--- stdout ---",
            result.stdout,
            "--- stderr ---",
            result.stderr,
        ]
        raise RuntimeError("\n".join(message))
    return result


def main() -> None:
    """Smoke-test an installed ABMForge wheel from outside the source tree."""

    import abmforge

    installed_version = version("abmforge")
    if abmforge.__version__ != installed_version:
        raise AssertionError(
            f"Package version mismatch: {abmforge.__version__!r} != {installed_version!r}"
        )

    dist = distribution("abmforge")
    files = {str(file) for file in dist.files or []}

    required_files = {
        "abmforge/py.typed",
        "abmforge/templates/builtin/grid/configs/baseline.yaml",
        "abmforge/templates/builtin/grid/configs/experiment.yaml",
        "abmforge/templates/builtin/grid/model/model.py",
    }
    missing = sorted(required_files - files)
    if missing:
        raise AssertionError(f"Installed wheel is missing package data: {missing}")

    run([sys.executable, "-m", "abmforge.cli.main", "--version"])
    run([sys.executable, "-m", "abmforge.cli.main", "info"])
    run([sys.executable, "-m", "abmforge.cli.main", "cite"])
    templates = run([sys.executable, "-m", "abmforge.cli.main", "templates", "--json"]).stdout
    template_names = {item["name"] for item in json.loads(templates)}
    if "grid" not in template_names:
        raise AssertionError(f"Grid template not found in installed package: {template_names}")

    with tempfile.TemporaryDirectory(prefix="abmforge-wheel-smoke-") as temp_dir:
        project = Path(temp_dir) / "smoke-study"
        run(
            [
                sys.executable,
                "-m",
                "abmforge.cli.main",
                "new",
                str(project),
                "--template",
                "grid",
            ]
        )

        expected_project_files = [
            project / "configs" / "baseline.yaml",
            project / "configs" / "experiment.yaml",
            project / "model" / "model.py",
            project / "tests",
        ]
        missing_project_files = [
            str(path.relative_to(project)) for path in expected_project_files if not path.exists()
        ]
        if missing_project_files:
            raise AssertionError(
                f"Generated project is missing expected files: {missing_project_files}"
            )

        archive = project / "outputs" / "baseline"
        run(
            [
                sys.executable,
                "-m",
                "abmforge.cli.main",
                "run",
                "configs/baseline.yaml",
                "--archive",
                str(archive),
                "--overwrite",
            ],
            cwd=project,
        )
        run(
            [
                sys.executable,
                "-m",
                "abmforge.cli.main",
                "validate",
                str(archive),
            ],
            cwd=project,
        )

        required_archive_files = [
            archive / "manifest.json",
            archive / "dataset_schema.json",
            archive / "run_index.json",
            archive / "configs" / "scenario.yaml",
            archive / "data" / "runs.json",
        ]
        missing_archive_files = [
            str(path.relative_to(archive)) for path in required_archive_files if not path.exists()
        ]
        if missing_archive_files:
            raise AssertionError(
                f"Generated archive is missing expected files: {missing_archive_files}"
            )

        # Keep the temporary directory clean on Windows when run locally.
        shutil.rmtree(project, ignore_errors=True)

    print(f"Installed ABMForge wheel smoke test passed for version {installed_version}")


if __name__ == "__main__":
    main()
