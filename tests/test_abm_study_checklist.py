from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "abm-study-checklist.md"


def test_abm_study_checklist_doc_exists() -> None:
    assert DOC.exists(), "docs/abm-study-checklist.md should exist"


def test_abm_study_checklist_covers_core_model_reporting_topics() -> None:
    text = DOC.read_text(encoding="utf-8")

    for term in [
        "Model purpose",
        "Research question",
        "Agents",
        "Environment",
        "Scheduling",
        "Parameters",
        "Initial conditions",
        "Randomness and Seeds",
        "Scenario and Experiment Design",
    ]:
        assert term in text


def test_abm_study_checklist_covers_archive_and_reproducibility() -> None:
    text = DOC.read_text(encoding="utf-8")

    for term in [
        "manifest.json",
        "dataset_schema.json",
        "run_index.json",
        "abmforge validate outputs/experiment_archive",
        "ABMForge version",
        "Python version",
        "source commit hash",
        "Reproducibility Package",
    ]:
        assert term in text


def test_abm_study_checklist_covers_analysis_and_validity_cautions() -> None:
    text = DOC.read_text(encoding="utf-8")

    for term in [
        "load_archive_tables",
        "summarize_metric_by_parameters",
        "Robustness",
        "Sensitivity",
        "Calibration",
        "Validation",
        "Do not treat successful execution or archive validation as model validation",
        "scientific validity",
    ]:
        assert term in text


def test_abm_study_checklist_covers_manuscript_and_availability() -> None:
    text = DOC.read_text(encoding="utf-8")

    for term in [
        "Manuscript Reporting Checklist",
        "Code and Data Availability",
        "Software citation",
        "Archive availability",
        "Reviewer-Facing Quick Check",
        "limitations",
    ]:
        assert term in text


def test_abm_study_checklist_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "ABM Study Checklist" in nav
    assert "abm-study-checklist.md" in nav


def test_researcher_quickstart_mentions_abm_study_checklist() -> None:
    text = (ROOT / "docs" / "researcher-quickstart.md").read_text(encoding="utf-8")

    assert "ABM Study Checklist" in text
    assert "abm-study-checklist.md" in text
