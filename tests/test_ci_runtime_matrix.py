from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_main_ci_declared_python_matrix_matches_supported_versions() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    for version in ["3.10", "3.11", "3.12", "3.13"]:
        assert version in workflow


def test_package_smoke_ci_checks_supported_runtime_edges() -> None:
    workflow = (ROOT / ".github" / "workflows" / "package-smoke.yml").read_text(encoding="utf-8")

    assert "3.10" in workflow
    assert "3.13" in workflow
    assert "python -m build" in workflow
    assert "twine check" in workflow
    assert "smoke_installed_package.py" in workflow
