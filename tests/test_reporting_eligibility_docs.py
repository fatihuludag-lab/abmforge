from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTING_DOC = ROOT / "docs" / "reporting.md"
FAILURE_HANDLING_DOC = ROOT / "docs" / "failure-handling.md"


def _normalized() -> str:
    text = REPORTING_DOC.read_text(encoding="utf-8")
    return " ".join(text.split())


def test_reporting_separates_status_and_analysis_eligibility() -> None:
    text = _normalized()

    expected = [
        "Execution status is reported independently from analysis eligibility",
        "its execution status is `completed` or `stopped`",
        "has at least one numeric final model metric",
        "execution status and analysis eligibility as separate concepts",
    ]

    for statement in expected:
        assert statement in text


def test_reporting_documents_analysis_eligibility_artifact() -> None:
    text = _normalized()

    expected = [
        "`analysis_eligibility.csv`",
        "`analysis_eligible`",
        "`exclusion_reason`",
        "`numeric_metric_count`",
        "`execution_failed`",
        "`execution_status_not_eligible`",
        "`no_numeric_final_metrics`",
        "`missing_run_id`",
    ]

    for statement in expected:
        assert statement in text


def test_reporting_does_not_classify_stopped_as_failed() -> None:
    text = _normalized()

    expected = [
        "`failed_runs.csv` contains execution failures only",
        "A `stopped` run is not classified as failed",
        "status-based selection bias",
    ]

    for statement in expected:
        assert statement in text


def test_reporting_documents_default_status_policy() -> None:
    text = _normalized()

    expected = [
        "| `completed` | Eligible when numeric final metrics are available |",
        "| `stopped` | Eligible when numeric final metrics are available |",
        "| `failed` | Excluded with `execution_failed` |",
        "Excluded with `execution_status_not_eligible`",
    ]

    for statement in expected:
        assert statement in text


def test_failure_handling_separates_status_and_eligibility() -> None:
    text = " ".join(FAILURE_HANDLING_DOC.read_text(encoding="utf-8").split())

    expected = [
        "separate execution status from analysis eligibility",
        "`analysis_eligibility.csv`",
        "`completed` and `stopped` runs are analysis-eligible",
        "`failed` runs are excluded with `execution_failed`",
        "A stopped run is not an execution failure",
    ]

    for statement in expected:
        assert statement in text


def test_failure_handling_removes_completed_only_policy() -> None:
    text = " ".join(FAILURE_HANDLING_DOC.read_text(encoding="utf-8").split())

    assert "Only runs whose status is exactly `completed`" not in text
    assert "analysis exclusion reasons" in text
    assert "study-specific eligibility rules" in text
