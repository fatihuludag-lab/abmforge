from __future__ import annotations

import csv
import json
from pathlib import Path

from abmforge.reporting import generate_experiment_report
from abmforge.repro.manifest import describe_file_artifact


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
        "run_id,status,parameters,error,exception_type\n"
        'run-1,completed,"{""transfer_probability"": 0.2}",,\n'
        'run-2,failed,"{""transfer_probability"": 0.5}",bad run,RuntimeError\n',
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
    assert report.analysis_eligibility_csv.exists()
    assert report.failed_runs_csv.exists()
    assert report.parameter_effects_csv.exists()
    assert report.primary_metric_rankings_csv.exists()

    summary_text = report.summary_markdown.read_text(encoding="utf-8")
    assert "ABMForge experiment report" in summary_text
    assert "Key findings" in summary_text
    assert "total_value" in summary_text
    assert "## Analysis eligibility" in summary_text
    assert "## Failed runs" in summary_text
    assert "failed or non-completed" not in summary_text
    assert "Primary metric parameter rankings" in summary_text

    metric_summary = report.metric_summary_csv.read_text(encoding="utf-8")
    assert "metric,run_count,mean,min,max" in metric_summary
    assert "total_value,1,6,6,6" in metric_summary
    assert "total_value,2,7,6,8" not in metric_summary

    parameter_effects = report.parameter_effects_csv.read_text(encoding="utf-8")
    assert "parameter,value,run_count,mean,min,max,difference_from_overall" in parameter_effects
    assert "transfer_probability" in parameter_effects
    assert "0.2,1,6,6,6,0" in parameter_effects
    assert "0.5" not in parameter_effects

    rankings = report.primary_metric_rankings_csv.read_text(encoding="utf-8")
    assert "rank_low_to_high,parameter_combination,run_count,mean,min,max" in rankings
    assert "transfer_probability" in rankings
    assert "0.2" in rankings
    assert "0.5" not in rankings

    failed_runs = report.failed_runs_csv.read_text(encoding="utf-8")
    assert "run-2" in failed_runs


def test_generate_experiment_report_finalizes_existing_manifest(
    tmp_path: Path,
) -> None:
    _write_demo_output(tmp_path)

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_version": "reproducibility-manifest-v1",
                "artifacts": [],
                "artifact_count": 0,
            }
        ),
        encoding="utf-8",
    )

    report = generate_experiment_report(tmp_path)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifact_paths = {artifact["path"] for artifact in manifest["artifacts"]}

    expected_report_paths = {
        report.summary_markdown.relative_to(tmp_path).as_posix(),
        report.metric_summary_csv.relative_to(tmp_path).as_posix(),
        report.run_status_csv.relative_to(tmp_path).as_posix(),
        report.failed_runs_csv.relative_to(tmp_path).as_posix(),
        report.parameter_effects_csv.relative_to(tmp_path).as_posix(),
        report.primary_metric_rankings_csv.relative_to(tmp_path).as_posix(),
    }

    assert expected_report_paths <= artifact_paths
    assert manifest["artifact_count"] == len(manifest["artifacts"])


def test_report_finalization_preserves_existing_artifact_checksums(
    tmp_path: Path,
) -> None:
    _write_demo_output(tmp_path)

    tracked_path = tmp_path / "data" / "runs.csv"
    tracked_artifact = describe_file_artifact(
        tracked_path,
        root=tmp_path,
        role="dataset_table",
    )
    original_sha256 = tracked_artifact["sha256"]

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_version": "reproducibility-manifest-v1",
                "artifacts": [tracked_artifact],
                "artifact_count": 1,
            }
        ),
        encoding="utf-8",
    )

    tracked_path.write_text(
        tracked_path.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )

    report = generate_experiment_report(tmp_path)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = {artifact["path"]: artifact for artifact in manifest["artifacts"]}

    assert artifacts["data/runs.csv"]["sha256"] == original_sha256
    assert report.summary_markdown.relative_to(tmp_path).as_posix() in artifacts
    assert manifest["artifact_count"] == len(manifest["artifacts"])


def _read_report_csv(path: Path) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


def _append_run(
    output_dir: Path,
    *,
    run_id: str,
    status: str,
    transfer_probability: float,
) -> None:
    runs_path = output_dir / "data" / "runs.csv"
    row = f'{run_id},{status},"{{""transfer_probability"": {transfer_probability}}}",,\n'

    runs_path.write_text(
        runs_path.read_text(encoding="utf-8") + row,
        encoding="utf-8",
    )


def _append_model_metric(
    output_dir: Path,
    *,
    run_id: str,
    step: int,
    metric: str,
    value: str,
) -> None:
    records_path = output_dir / "data" / "model_records.csv"

    records_path.write_text(
        records_path.read_text(encoding="utf-8") + f"{run_id},{step},{metric},{value}\n",
        encoding="utf-8",
    )


def test_metric_reports_include_completed_and_stopped_runs(
    tmp_path: Path,
) -> None:
    _write_demo_output(tmp_path)

    _append_run(
        tmp_path,
        run_id="run-3",
        status="stopped",
        transfer_probability=0.8,
    )
    _append_model_metric(
        tmp_path,
        run_id="run-3",
        step=3,
        metric="total_value",
        value="100",
    )

    report = generate_experiment_report(tmp_path)

    metric_rows = {row["metric"]: row for row in _read_report_csv(report.metric_summary_csv)}
    total_value = metric_rows["total_value"]

    assert total_value["run_count"] == "2"
    assert float(total_value["mean"]) == 53.0
    assert float(total_value["min"]) == 6.0
    assert float(total_value["max"]) == 100.0

    parameter_rows = _read_report_csv(report.parameter_effects_csv)
    parameter_values = {
        row["value"] for row in parameter_rows if row["parameter"] == "transfer_probability"
    }

    assert parameter_values == {"0.2", "0.8"}

    ranking_text = report.primary_metric_rankings_csv.read_text(encoding="utf-8")

    assert "0.2" in ranking_text
    assert "0.8" in ranking_text
    assert "0.5" not in ranking_text

    failed_rows = _read_report_csv(report.failed_runs_csv)

    assert {row["run_id"] for row in failed_rows} == {"run-2"}

    assert {row["status"] for row in failed_rows} == {"failed"}


def test_report_separates_status_from_analysis_eligibility(
    tmp_path: Path,
) -> None:
    _write_demo_output(tmp_path)

    _append_run(
        tmp_path,
        run_id="run-3",
        status="stopped",
        transfer_probability=0.8,
    )
    _append_model_metric(
        tmp_path,
        run_id="run-3",
        step=3,
        metric="total_value",
        value="100",
    )

    report = generate_experiment_report(tmp_path)

    eligibility_rows = {
        row["run_id"]: row for row in _read_report_csv(report.analysis_eligibility_csv)
    }

    assert eligibility_rows["run-1"] == {
        "run_id": "run-1",
        "status": "completed",
        "analysis_eligible": "true",
        "exclusion_reason": "",
        "numeric_metric_count": "1",
    }
    assert eligibility_rows["run-2"]["analysis_eligible"] == "false"
    assert eligibility_rows["run-2"]["exclusion_reason"] == "execution_failed"

    assert eligibility_rows["run-3"] == {
        "run_id": "run-3",
        "status": "stopped",
        "analysis_eligible": "true",
        "exclusion_reason": "",
        "numeric_metric_count": "1",
    }

    summary = report.summary_markdown.read_text(encoding="utf-8")

    expected_lines = [
        "## Analysis eligibility",
        "- total runs: 3",
        "- completed runs: 1",
        "- stopped runs: 1",
        "- failed runs: 1",
        "- analysis-eligible runs: 2",
        "- analysis-excluded runs: 1",
    ]

    for line in expected_lines:
        assert line in summary


def test_terminal_run_without_numeric_metrics_is_excluded_with_reason(
    tmp_path: Path,
) -> None:
    _write_demo_output(tmp_path)

    _append_run(
        tmp_path,
        run_id="run-4",
        status="completed",
        transfer_probability=0.9,
    )

    report = generate_experiment_report(tmp_path)

    eligibility_rows = {
        row["run_id"]: row for row in _read_report_csv(report.analysis_eligibility_csv)
    }

    assert eligibility_rows["run-4"] == {
        "run_id": "run-4",
        "status": "completed",
        "analysis_eligible": "false",
        "exclusion_reason": "no_numeric_final_metrics",
        "numeric_metric_count": "0",
    }

    failed_ids = {row["run_id"] for row in _read_report_csv(report.failed_runs_csv)}

    assert failed_ids == {"run-2"}


def test_stopped_run_with_invalid_metric_is_excluded_but_not_failed(
    tmp_path: Path,
) -> None:
    _write_demo_output(tmp_path)

    _append_run(
        tmp_path,
        run_id="run-5",
        status="stopped",
        transfer_probability=0.9,
    )
    _append_model_metric(
        tmp_path,
        run_id="run-5",
        step=3,
        metric="total_value",
        value="not-a-number",
    )

    report = generate_experiment_report(tmp_path)

    eligibility_rows = {
        row["run_id"]: row for row in _read_report_csv(report.analysis_eligibility_csv)
    }

    assert eligibility_rows["run-5"] == {
        "run_id": "run-5",
        "status": "stopped",
        "analysis_eligible": "false",
        "exclusion_reason": "no_numeric_final_metrics",
        "numeric_metric_count": "0",
    }

    failed_ids = {row["run_id"] for row in _read_report_csv(report.failed_runs_csv)}

    assert failed_ids == {"run-2"}
