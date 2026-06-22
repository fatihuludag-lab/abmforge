from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def sdist_members(tmp_path_factory: pytest.TempPathFactory) -> set[str]:
    dist_dir = tmp_path_factory.mktemp("sdist") / "dist"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--sdist",
            "--outdir",
            str(dist_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, (
        "sdist build failed\n"
        f"command: {completed.args}\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
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


def test_sdist_includes_project_metadata_and_license(
    sdist_members: set[str],
) -> None:
    for relative_path in [
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "RELEASE_NOTES.md",
        "CITATION.cff",
        "codemeta.json",
        "pyproject.toml",
    ]:
        assert has_member(sdist_members, relative_path)


def test_sdist_includes_docs_examples_model_zoo_and_tests(
    sdist_members: set[str],
) -> None:
    assert has_directory_member(sdist_members, "docs")
    assert has_directory_member(sdist_members, "examples")
    assert has_directory_member(sdist_members, "model_zoo")
    assert has_directory_member(sdist_members, "tests")


def test_sdist_includes_representative_python_sources(
    sdist_members: set[str],
) -> None:
    assert any(member.endswith("/examples/wealth_model/run.py") for member in sdist_members)
    assert any("/model_zoo/" in member and member.endswith(".py") for member in sdist_members)
    assert any(member.endswith("/tests/test_import.py") for member in sdist_members)
