from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_VERSION = "0.3.0a1"


def test_pyproject_version_is_first_public_alpha() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)

    assert match is not None
    assert match.group(1) == TARGET_VERSION
    assert not match.group(1).endswith(".dev0")


def test_release_metadata_strict_check_passes_for_pypi_alpha() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_release_metadata.py", "--strict"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Release metadata check passed." in result.stdout


def test_citation_and_codemeta_versions_match_pypi_alpha() -> None:
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    codemeta = json.loads((ROOT / "codemeta.json").read_text(encoding="utf-8"))

    assert TARGET_VERSION in citation
    assert (
        codemeta.get("softwareVersion") == TARGET_VERSION
        or codemeta.get("version") == TARGET_VERSION
    )


def test_changelog_mentions_pypi_alpha_release() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert f"## [{TARGET_VERSION}]" in changelog
    assert "production PyPI alpha release" in changelog
    assert "pip install abmforge" in changelog
    assert "v0.3.0a1" in changelog


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


def test_pypi_alpha_release_docs_are_present_and_listed() -> None:
    docs = (ROOT / "docs" / "pypi-alpha-release.md").read_text(encoding="utf-8")
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    for term in [
        "PyPI Alpha Release Preparation",
        "v0.3.0a1",
        "python -m pip install abmforge",
        "Trusted Publishing",
        "Environment name: pypi",
        "Production Publish Gate",
        "git tag v0.3.0a1",
        "PyPI Install Smoke",
    ]:
        assert term in docs

    assert "PyPI Alpha Release" in nav
    assert "pypi-alpha-release.md" in nav
