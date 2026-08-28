from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RELEASED_ALPHA_VERSION = "0.3.0a1"
RELEASED_ALPHA_TAG = f"v{RELEASED_ALPHA_VERSION}"
RELEASED_ALPHA_DATE = "2026-06-30"


def current_pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)

    assert match is not None
    return match.group(1)


def test_current_tree_does_not_reuse_first_public_alpha_version() -> None:
    assert current_pyproject_version() != RELEASED_ALPHA_VERSION


def test_release_metadata_strict_check_passes_for_current_tree() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_release_metadata.py", "--strict"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Release metadata check passed." in result.stdout


def test_first_public_alpha_is_recorded_as_released() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert f"## [{RELEASED_ALPHA_VERSION}] - {RELEASED_ALPHA_DATE}" in changelog
    assert "production PyPI alpha release" in changelog
    assert "pip install abmforge" in changelog
    assert RELEASED_ALPHA_TAG in changelog


def test_release_workflow_has_manual_production_pypi_gate() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "publish_pypi" in workflow
    assert "name: Publish to PyPI" in workflow
    assert "environment:" in workflow
    assert "name: pypi" in workflow
    assert "id-token: write" in workflow
    assert "startsWith(github.ref, 'refs/tags/v')" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "password:" not in workflow
    assert "TWINE_PASSWORD" not in workflow


def test_pypi_install_smoke_workflow_is_manual_and_non_publishing() -> None:
    workflow = (ROOT / ".github" / "workflows" / "pypi-install-smoke.yml").read_text(
        encoding="utf-8"
    )

    assert "name: PyPI Install Smoke" in workflow
    assert "workflow_dispatch:" in workflow
    assert "push:" not in workflow
    assert "pull_request:" not in workflow
    assert "python -m pip install" in workflow
    assert "scripts/smoke_installed_package.py" in workflow
    assert "pypa/gh-action-pypi-publish" not in workflow


def test_first_public_alpha_release_runbook_is_preserved() -> None:
    docs = (ROOT / "docs" / "pypi-alpha-release.md").read_text(encoding="utf-8")
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    for term in [
        "PyPI Alpha Release Preparation",
        RELEASED_ALPHA_TAG,
        "python -m pip install abmforge",
        "Trusted Publishing",
        "Environment name: pypi",
        "Production Publish Gate",
        f"git tag {RELEASED_ALPHA_TAG}",
        "PyPI Install Smoke",
    ]:
        assert term in docs

    assert "PyPI Alpha Release" in nav
    assert "pypi-alpha-release.md" in nav
