from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "reference-reproducible-workflow.md"


def test_reference_reproducible_workflow_doc_exists() -> None:
    assert DOC_PATH.exists()


def test_reference_reproducible_workflow_is_in_mkdocs_nav() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "reference-reproducible-workflow.md" in mkdocs


def test_reference_reproducible_workflow_documents_core_commands() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "abmforge run examples/scenarios/wealth_baseline.yaml" in text
    assert "abmforge validate outputs/wealth_baseline_reference" in text
    assert "abmforge summarize outputs/wealth_baseline_reference" in text
    assert "python -m pip install -e" in text


def test_reference_reproducible_workflow_states_alpha_limits() -> None:
    text = DOC_PATH.read_text(encoding="utf-8").lower()

    assert "alpha-stage software" in text
    assert "does not yet prove full independent reproduction" in text
    assert "source code" in text
    assert "input data" in text
    assert "execution environment" in text
