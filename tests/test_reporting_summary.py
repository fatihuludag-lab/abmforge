from __future__ import annotations

import json
from pathlib import Path

from abmforge.reporting import generate_experiment_report


def _write_demo_output(root: Path) -> None:
    (root / "reports").mkdir(parents=True)
    (root / "data").mkdir(parents=True)

    (root / "reports" / "experiment_summary.json").write_text(
        json.dumps(
            {
                "name": "demo",
                "model": "study_model.DemoModel",
                "steps": 3,
                "seed_count": 2,
                "run_count_expected": 2,
                "primary_metric": "total_value",
            }
        ),
        encoding="utf-8",
    )
    (root / "data" / "runs.csv").write_text(
        "run_id,status,error,exception_type\n"
        "run-1,completed,,\n"
        "run-2,failed,bad run,RuntimeError\n",
        encoding="utf-8",
    )
    (root / "data" / "model_records.csv").write_text(
        "run_id,step,metric,value\n"
        "run-1,1,total_value,2\n"
        "run-1,3,total_value,6\n"
        "run-2,1,total_value,4\n"
        "run-2,3,total_value,8\n",
        encoding="utf-8",
    )
    (root / "data" / "errors.csv").write_text(
        "run_id,message,exception_type\n",
        encoding="utf-8",
    )


def test_generate_experiment_report_writes_summary_files(tmp_path: Path) -> None:
    _write_demo_output(tmp_path)

    report = generate_experiment_report(tmp_path)

    assert report.summary_markdown.exists()
    assert report.metric_summary_csv.exists()
    assert report.run_status_csv.exists()
    assert report.failed_runs_csv.exists()

    summary_text = report.summary_markdown.read_text(encoding="utf-8")
    assert "ABMForge experiment report" in summary_text
    assert "total_value" in summary_text
    assert "failed or non-completed" in summary_text

    metric_summary = report.metric_summary_csv.read_text(encoding="utf-8")
    assert "metric,run_count,mean,min,max" in metric_summary
    assert "total_value,2,7,6,8" in metric_summary

    failed_runs = report.failed_runs_csv.read_text(encoding="utf-8")
    assert "run-2" in failed_runs
