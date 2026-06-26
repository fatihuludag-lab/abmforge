from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def current_pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    assert match is not None
    return match.group(1)


def test_changelog_mentions_current_declared_version() -> None:
    version = current_pyproject_version()
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert f"## [{version}]" in changelog or f"## {version}" in changelog
    assert "Release metadata" in changelog
    assert "Public API stability policy" in changelog
    assert "Benchmark reference suite scaffold" in changelog
    assert "Researcher quickstart" in changelog


def test_strict_release_metadata_check_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_release_metadata.py", "--strict"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Release metadata check passed." in result.stdout


def test_release_candidate_prep_doc_exists_and_is_conservative() -> None:
    text = (ROOT / "docs" / "release-candidate-prep.md").read_text(encoding="utf-8")

    for term in [
        "Release Candidate Preparation",
        "python scripts/check_release_metadata.py --strict",
        "TestPyPI",
        "not automatically",
        "Known Alpha Limitations",
        "Maintainer Checklist",
    ]:
        assert term in text


def test_release_candidate_prep_doc_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Release Candidate Preparation" in nav
    assert "release-candidate-prep.md" in nav
