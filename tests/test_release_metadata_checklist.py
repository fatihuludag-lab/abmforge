from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_checklist_documentation_exists_and_is_actionable() -> None:
    docs = (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")

    assert "Release Checklist" in docs
    assert "python scripts/check_release_metadata.py" in docs
    assert "python -m build" in docs
    assert "python -m twine check dist/*" in docs
    assert "TestPyPI Dry Run" in docs
    assert "Changelog Policy" in docs
    assert "Citation Metadata" in docs


def test_release_checklist_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Release Checklist" in nav
    assert "release-checklist.md" in nav


def test_release_metadata_checker_exists_and_mentions_core_sources() -> None:
    script = (ROOT / "scripts" / "check_release_metadata.py").read_text(encoding="utf-8")

    assert "pyproject.toml" in script
    assert "src/abmforge runtime" in script
    assert "CITATION.cff" in script
    assert "codemeta.json" in script
    assert "CHANGELOG.md" in script
    assert "--strict" in script


def test_release_metadata_checker_passes_in_non_strict_mode() -> None:
    script = ROOT / "scripts" / "check_release_metadata.py"

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Release metadata check passed." in result.stdout
