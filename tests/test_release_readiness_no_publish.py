from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_version_consistency_script_supports_current_runtime_version_contract() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/check_version_consistency.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Version consistency check passed." in completed.stdout


def test_no_publish_release_readiness_doc_exists_and_defers_uploads() -> None:
    doc = (ROOT / "docs" / "release-readiness-no-publish.md").read_text(encoding="utf-8")

    required_terms = [
        "credential-free",
        "python scripts/check_version_consistency.py",
        "python scripts/check_release_metadata.py --strict",
        "python -m build",
        "python -m twine check dist/*",
        "publish_testpypi=true",
        "publish_pypi=true",
        "twine upload",
        "deferred",
    ]

    for term in required_terms:
        assert term in doc


def test_release_workflow_keeps_publish_jobs_explicitly_gated() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "publish_testpypi:" in workflow
    assert "publish_pypi:" in workflow
    assert "inputs.publish_testpypi" in workflow
    assert "inputs.publish_pypi" in workflow
    assert "startsWith(github.ref, 'refs/tags/v')" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
