from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_workflow_exists_and_builds_distributions() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "name: Release" in workflow
    assert "workflow_dispatch:" in workflow
    assert "tags:" in workflow
    assert '"v*"' in workflow
    assert "python -m build" in workflow
    assert "python -m twine check dist/*" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "dist/*" in workflow


def test_release_workflow_testpypi_publish_is_manual_and_oidc_based() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "publish_testpypi" in workflow
    expected_guard = "if: github.event_name == 'workflow_dispatch' && inputs.publish_testpypi"
    assert expected_guard in workflow
    assert "environment:" in workflow
    assert "name: testpypi" in workflow
    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "https://test.pypi.org/legacy/" in workflow
    assert "password:" not in workflow
    assert "TWINE_PASSWORD" not in workflow


def test_releasing_documentation_describes_safe_release_path() -> None:
    docs = (ROOT / "docs" / "releasing.md").read_text(encoding="utf-8")

    assert "TestPyPI" in docs
    assert "trusted publisher" in docs.lower()
    assert "publish_testpypi" in docs
    assert "does not automatically publish to production PyPI" in docs
    assert "First Safe Release Path" in docs


def test_releasing_documentation_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Release Process" in nav
    assert "releasing.md" in nav
