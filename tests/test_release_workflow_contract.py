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
    assert "publish_pypi" in docs
    assert "valid version tag" in docs.lower()
    assert "only one publication target" in docs.lower()
    assert "quality gates" in docs.lower()
    assert "SHA256SUMS" in docs
    assert "First Safe Release Path" in docs


def test_releasing_documentation_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Release Process" in nav
    assert "releasing.md" in nav


def test_release_workflow_serializes_same_ref_without_cancelling() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "concurrency:" in workflow
    assert "group: release-${{ github.ref }}" in workflow
    assert "cancel-in-progress: false" in workflow


def test_release_workflow_runs_quality_gates_before_build() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "quality:" in workflow
    assert "python scripts/check_version_consistency.py" in workflow
    assert "python scripts/check_release_metadata.py --strict" in workflow
    assert "ruff format --check src tests examples scripts" in workflow
    assert "ruff check src tests examples scripts" in workflow
    assert "mypy src" in workflow
    assert "pytest --cov=abmforge" in workflow
    assert "mkdocs build --strict" in workflow
    assert "needs: quality" in workflow


def test_release_workflow_validates_tag_against_package_version() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "scripts/check_release_tag.py" in workflow
    assert "GITHUB_REF_NAME" in workflow
    assert "--tag" in workflow


def test_release_workflow_smoke_tests_the_built_wheel_before_upload() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    smoke_command = (
        "/tmp/abmforge-release-smoke/bin/python "
        '"$GITHUB_WORKSPACE/scripts/smoke_installed_package.py"'
    )

    assert "Install built wheel in a clean virtual environment" in workflow
    assert "python -m venv /tmp/abmforge-release-smoke" in workflow
    assert "pip install dist/*.whl" in workflow
    assert smoke_command in workflow


def test_release_workflow_rejects_conflicting_publish_targets() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "Validate manual publish selection" in workflow
    assert "PUBLISH_TESTPYPI: ${{ inputs.publish_testpypi }}" in workflow
    assert "PUBLISH_PYPI: ${{ inputs.publish_pypi }}" in workflow
    assert "Select only one publication target per workflow run." in workflow


def test_release_workflow_requires_tag_ref_for_production_publish() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "Package-index publishing requires dispatching" in workflow
    assert '[[ "$GITHUB_REF" != refs/tags/v* ]]' in workflow

    expected_guard = (
        "if: github.event_name == 'workflow_dispatch' && "
        "inputs.publish_pypi && startsWith(github.ref, 'refs/tags/v')"
    )
    assert expected_guard in workflow


def test_release_workflow_generates_and_uploads_checksums() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "sha256sum dist/* > SHA256SUMS" in workflow
    assert "name: abmforge-checksums" in workflow
    assert "path: SHA256SUMS" in workflow


def test_publish_jobs_verify_downloaded_distribution_checksums() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert workflow.count("name: Download checksum artifact") == 2
    assert workflow.count("sha256sum --check SHA256SUMS") == 2


def test_release_workflow_requires_tag_ref_for_any_publish() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "Package-index publishing requires dispatching" in workflow
    assert workflow.count("startsWith(github.ref, 'refs/tags/v')") == 2


def test_release_docs_require_valid_tag_for_testpypi_publish() -> None:
    documents = [
        ROOT / "docs" / "release-candidate-prep.md",
        ROOT / "docs" / "release-checklist.md",
        ROOT / "docs" / "testpypi-dry-run.md",
        ROOT / "docs" / "release-readiness-no-publish.md",
    ]

    for document in documents:
        content = document.read_text(encoding="utf-8").lower()

        assert "testpypi" in content
        assert "valid version tag" in content, document
