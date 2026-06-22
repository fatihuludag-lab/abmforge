from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_sdist(tmp_path: Path) -> set[str]:
    dist_dir = tmp_path / "dist"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--sdist",
            "--no-isolation",
            "--outdir",
            str(dist_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, (
        f"sdist build failed\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )

    sdists = sorted(dist_dir.glob("*.tar.gz"))
    assert len(sdists) == 1

    with tarfile.open(sdists[0], "r:gz") as archive:
        return {member.name for member in archive.getmembers()}


def has_member(members: set[str], relative_path: str) -> bool:
    return any(member.endswith(f"/{relative_path}") for member in members)


def has_directory_member(members: set[str], directory: str) -> bool:
    marker = f"/{directory.rstrip('/')}/"
    return any(marker in member for member in members)


def test_sdist_includes_project_metadata_and_license(tmp_path) -> None:
    members = build_sdist(tmp_path)

    for relative_path in [
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "RELEASE_NOTES.md",
        "CITATION.cff",
        "codemeta.json",
        "pyproject.toml",
    ]:
        assert has_member(members, relative_path)


def test_sdist_includes_docs_examples_model_zoo_and_tests(tmp_path) -> None:
    members = build_sdist(tmp_path)

    assert has_directory_member(members, "docs")
    assert has_directory_member(members, "examples")
    assert has_directory_member(members, "model_zoo")
    assert has_directory_member(members, "tests")


def test_sdist_includes_representative_python_sources(tmp_path) -> None:
    members = build_sdist(tmp_path)

    assert any(member.endswith("/examples/wealth_model/run.py") for member in members)
    assert any("/model_zoo/" in member and member.endswith(".py") for member in members)
    assert any(member.endswith("/tests/test_import.py") for member in members)
