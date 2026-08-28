from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_release_tag.py"


def current_pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    assert match is not None
    return match.group(1)


def _run_tag_check(tag: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--tag", tag],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_release_tag_checker_rejects_current_development_version() -> None:
    version = current_pyproject_version()
    assert ".dev" in version

    result = _run_tag_check(f"v{version}")

    assert result.returncode == 1
    assert "targets a development version" in result.stdout
    assert "Bump package metadata to a non-development version" in result.stdout


def test_release_tag_checker_rejects_version_mismatch() -> None:
    version = current_pyproject_version()
    result = _run_tag_check("v0.3.0")

    assert result.returncode == 1
    assert "does not match the package version" in result.stdout
    assert version in result.stdout


def test_release_tag_checker_rejects_malformed_tag() -> None:
    result = _run_tag_check("version-0.3.0a1")

    assert result.returncode == 1
    assert "Release tag must use the form" in result.stdout


def test_release_tag_checker_rejects_overbroad_v_prefix_tag() -> None:
    result = _run_tag_check("vnext")

    assert result.returncode == 1
    assert "Release tag must use the form" in result.stdout
