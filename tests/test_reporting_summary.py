from __future__ import annotations

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
    assert report.failed_runs_csv.exists()
    assert report.parameter_effects_csv.exists()
    assert report.primary_metric_rankings_csv.exists()

    summary_text = report.summary_markdown.read_text(encoding="utf-8")
    assert "ABMForge experiment report" in summary_text
    assert "Key findings" in summary_text
    assert "total_value" in summary_text
    assert "failed or non-completed" in summary_text
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


def test_metric_reports_include_only_completed_runs(tmp_path: Path) -> None:
    _write_demo_output(tmp_path)

    runs_path = tmp_path / "data" / "runs.csv"
    runs_path.write_text(
        runs_path.read_text(encoding="utf-8")
        + 'run-3,stopped,"{""transfer_probability"": 0.8}",,\n',
        encoding="utf-8",
    )

    model_records_path = tmp_path / "data" / "model_records.csv"
    model_records_path.write_text(
        model_records_path.read_text(encoding="utf-8") + "run-3,3,total_value,100\n",
        encoding="utf-8",
    )

    report = generate_experiment_report(tmp_path)

    metric_summary = report.metric_summary_csv.read_text(encoding="utf-8")
    parameter_effects = report.parameter_effects_csv.read_text(encoding="utf-8")
    rankings = report.primary_metric_rankings_csv.read_text(encoding="utf-8")
    failed_runs = report.failed_runs_csv.read_text(encoding="utf-8")

    assert "total_value,1,6,6,6" in metric_summary
    assert "100" not in metric_summary

    assert "0.2,1,6,6,6,0" in parameter_effects
    assert "0.5" not in parameter_effects
    assert "0.8" not in parameter_effects

    assert "0.2" in rankings
    assert "0.5" not in rankings
    assert "0.8" not in rankings

    assert "run-2" in failed_runs
    assert "run-3" in failed_runs
    assert "stopped" in failed_runs
