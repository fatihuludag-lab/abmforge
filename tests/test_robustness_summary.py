from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from abmforge.analysis.robustness import (
    RobustnessSummaryError,
    summarize_metric,
    summarize_metric_by_parameters,
    write_summary_csv,
)

ROOT = Path(__file__).resolve().parents[1]


def _write_robustness_archive(archive: Path) -> None:
    data_dir = archive / "data"
    data_dir.mkdir(parents=True)

    runs = [
        {
            "run_id": "r1",
            "parameters": {"peer_influence": 0.45, "seed": 1},
        },
        {
            "run_id": "r2",
            "parameters": {"peer_influence": 0.45, "seed": 2},
        },
        {
            "run_id": "r3",
            "parameters": {"peer_influence": 0.90, "seed": 1},
        },
    ]
    model_records = [
        {"run_id": "r1", "step": 0, "metric": "adoption_share", "value": 0.10},
        {"run_id": "r1", "step": 5, "metric": "adoption_share", "value": 0.40},
        {"run_id": "r2", "step": 0, "metric": "adoption_share", "value": 0.20},
        {"run_id": "r2", "step": 5, "metric": "adoption_share", "value": 0.60},
        {"run_id": "r3", "step": 0, "metric": "adoption_share", "value": 0.30},
        {"run_id": "r3", "step": 5, "metric": "adoption_share", "value": 0.90},
        {"run_id": "r3", "step": 5, "metric": "other_metric", "value": 100.0},
    ]

    (data_dir / "runs.json").write_text(json.dumps(runs), encoding="utf-8")
    (data_dir / "model_records.json").write_text(
        json.dumps(model_records),
        encoding="utf-8",
    )


def test_summarize_metric_uses_latest_value_per_run_by_default() -> None:
    records = [
        {"run_id": "r1", "step": 0, "metric": "x", "value": 1.0},
        {"run_id": "r1", "step": 2, "metric": "x", "value": 3.0},
        {"run_id": "r2", "step": 0, "metric": "x", "value": 5.0},
    ]

    summary = summarize_metric(records, metric="x")

    assert summary["count"] == 2
    assert summary["mean"] == 4.0
    assert summary["min"] == 3.0
    assert summary["max"] == 5.0


def test_summarize_metric_can_use_all_time_records() -> None:
    records = [
        {"run_id": "r1", "step": 0, "metric": "x", "value": 1.0},
        {"run_id": "r1", "step": 2, "metric": "x", "value": 3.0},
        {"run_id": "r2", "step": 0, "metric": "x", "value": 5.0},
    ]

    summary = summarize_metric(records, metric="x", latest_per_run=False)

    assert summary["count"] == 3
    assert summary["mean"] == 3.0


def test_summarize_metric_by_parameters_groups_latest_values(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _write_robustness_archive(archive)

    rows = summarize_metric_by_parameters(
        archive,
        metric="adoption_share",
        group_by=["peer_influence"],
    )

    assert len(rows) == 2

    low = next(row for row in rows if row["peer_influence"] == 0.45)
    high = next(row for row in rows if row["peer_influence"] == 0.90)

    assert low["count"] == 2
    assert low["mean"] == pytest.approx(0.5)
    assert low["std"] == pytest.approx(0.1414213562)
    assert high["count"] == 1
    assert high["mean"] == pytest.approx(0.9)


def test_write_summary_csv_writes_grouped_rows(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _write_robustness_archive(archive)

    rows = summarize_metric_by_parameters(
        archive,
        metric="adoption_share",
        group_by=["peer_influence"],
    )
    output = write_summary_csv(rows, tmp_path / "robustness.csv")

    with output.open(newline="", encoding="utf-8") as handle:
        loaded = list(csv.DictReader(handle))

    assert len(loaded) == 2
    assert "peer_influence" in loaded[0]
    assert "mean" in loaded[0]


def test_summarize_metric_raises_for_missing_metric() -> None:
    with pytest.raises(RobustnessSummaryError, match="missing"):
        summarize_metric(
            [{"run_id": "r1", "step": 0, "metric": "x", "value": 1.0}],
            metric="missing",
        )


def test_sensitivity_robustness_docs_are_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Sensitivity and Robustness" in nav
    assert "sensitivity-robustness.md" in nav
