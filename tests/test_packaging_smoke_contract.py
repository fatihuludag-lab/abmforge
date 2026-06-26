from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_package_smoke_workflow_exists() -> None:
    workflow = ROOT / ".github" / "workflows" / "package-smoke.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "Package Smoke" in text
    assert "python -m build" in text
    assert "python -m twine check dist/*" in text
    assert "pip install dist/*.whl" in text
    assert "scripts/smoke_installed_package.py" in text
    assert '"3.10"' in text
    assert '"3.13"' in text


def test_installed_package_smoke_script_checks_templates_and_archive() -> None:
    script = ROOT / "scripts" / "smoke_installed_package.py"
    text = script.read_text(encoding="utf-8")

    assert 'distribution("abmforge")' in text
    assert "abmforge/templates/builtin/grid/configs/baseline.yaml" in text
    assert 'templates", "--json"' in text
    assert '"new"' in text
    assert '"run"' in text
    assert '"validate"' in text
    assert "manifest.json" in text
    assert "dataset_schema.json" in text
    assert "run_index.json" in text
