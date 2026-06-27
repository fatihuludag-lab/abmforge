from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_testpypi_dry_run_docs_exist_and_are_conservative() -> None:
    text = (ROOT / "docs" / "testpypi-dry-run.md").read_text(encoding="utf-8")

    for term in [
        "TestPyPI Dry Run",
        "does not publish to production PyPI",
        "Trusted Publishing",
        "publish_testpypi=true",
        "Environment name: testpypi",
        "pending trusted publisher",
        "--index-url https://test.pypi.org/simple/",
        "--extra-index-url https://pypi.org/simple/",
        "Production PyPI Gate",
    ]:
        assert term in text


def test_testpypi_dry_run_docs_include_installed_cli_smoke() -> None:
    text = (ROOT / "docs" / "testpypi-dry-run.md").read_text(encoding="utf-8")

    for command in [
        "abmforge --version",
        "abmforge info",
        "abmforge cite",
        "abmforge templates --json",
        "abmforge new abmforge-smoke-study --template grid",
        "abmforge validate outputs/archive",
        "abmforge summarize outputs/archive --json",
    ]:
        assert command in text


def test_testpypi_install_smoke_workflow_is_manual_only() -> None:
    workflow = (ROOT / ".github" / "workflows" / "testpypi-install-smoke.yml").read_text(
        encoding="utf-8"
    )

    assert "name: TestPyPI Install Smoke" in workflow
    assert "workflow_dispatch:" in workflow
    assert "push:" not in workflow
    assert "pull_request:" not in workflow
    assert "package_version" in workflow


def test_testpypi_install_smoke_workflow_installs_from_testpypi() -> None:
    workflow = (ROOT / ".github" / "workflows" / "testpypi-install-smoke.yml").read_text(
        encoding="utf-8"
    )

    assert "--index-url https://test.pypi.org/simple/" in workflow
    assert "--extra-index-url https://pypi.org/simple/" in workflow
    assert "scripts/smoke_installed_package.py" in workflow
    assert "pypa/gh-action-pypi-publish" not in workflow
    assert "repository-url: https://upload.pypi.org/legacy/" not in workflow


def test_testpypi_dry_run_docs_are_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "TestPyPI Dry Run" in nav
    assert "testpypi-dry-run.md" in nav
