from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_release_tag.py"


def _run_tag_check(tag: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--tag", tag],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_release_tag_checker_accepts_current_package_version() -> None:
    result = _run_tag_check("v0.3.0a1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Release tag check passed: v0.3.0a1" in result.stdout


def test_release_tag_checker_rejects_version_mismatch() -> None:
    result = _run_tag_check("v0.3.0")

    assert result.returncode == 1
    assert "does not match the package version" in result.stdout
    assert "0.3.0a1" in result.stdout


def test_release_tag_checker_rejects_malformed_tag() -> None:
    result = _run_tag_check("version-0.3.0a1")

    assert result.returncode == 1
    assert "Release tag must use the form" in result.stdout


def test_release_tag_checker_rejects_overbroad_v_prefix_tag() -> None:
    result = _run_tag_check("vnext")

    assert result.returncode == 1
    assert "Release tag must use the form" in result.stdout
