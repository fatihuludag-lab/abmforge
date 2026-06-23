from pathlib import Path

from abmforge.data.dataset import Dataset
from abmforge.experiment import (
    ExperimentArchive,
    summarize_archive_runs,
    summarize_run_records,
)


def _dataset_with_runs() -> Dataset:
    dataset = Dataset(run_id="run-001")
    dataset.add_run(
        run_id="run-001",
        scenario="baseline",
        model_name="ToyModel",
        parameters={"alpha": 0.2},
        seed=1,
        status="completed",
        started_at="2026-06-22T10:00:00+00:00",
        ended_at="2026-06-22T10:00:01+00:00",
        steps=5,
        stop_reason=None,
    )
    dataset.add_run(
        run_id="run-002",
        scenario="baseline",
        model_name="ToyModel",
        parameters={"alpha": 0.2},
        seed=2,
        status="completed",
        started_at="2026-06-22T10:01:00+00:00",
        ended_at="2026-06-22T10:01:01+00:00",
        steps=10,
        stop_reason=None,
    )
    dataset.add_run(
        run_id="run-003",
        scenario="policy",
        model_name="ToyModel",
        parameters={"alpha": 0.5},
        seed=3,
        status="failed",
        started_at="2026-06-22T10:02:00+00:00",
        ended_at="2026-06-22T10:02:01+00:00",
        steps=3,
        stop_reason="error",
    )
    return dataset


def test_summarize_run_records_counts_status_scenario_model_and_steps() -> None:
    records = [
        {
            "run_id": "run-001",
            "scenario": "baseline",
            "model_name": "ToyModel",
            "seed": 1,
            "status": "completed",
            "steps": 5,
        },
        {
            "run_id": "run-002",
            "scenario": "baseline",
            "model_name": "ToyModel",
            "seed": 2,
            "status": "completed",
            "steps": 10,
        },
        {
            "run_id": "run-003",
            "scenario": "policy",
            "model_name": "ToyModel",
            "seed": 3,
            "status": "failed",
            "steps": 3,
        },
    ]

    summary = summarize_run_records(records)

    assert summary == {
        "run_count": 3,
        "completed_count": 2,
        "failed_count": 1,
        "status_counts": {"completed": 2, "failed": 1},
        "scenario_counts": {"baseline": 2, "policy": 1},
        "model_counts": {"ToyModel": 3},
        "seed_count": 3,
        "step_summary": {
            "count": 3,
            "min": 3.0,
            "max": 10.0,
            "mean": 6.0,
        },
    }


def test_summarize_run_records_handles_empty_records() -> None:
    summary = summarize_run_records([])

    assert summary == {
        "run_count": 0,
        "completed_count": 0,
        "failed_count": 0,
        "status_counts": {},
        "scenario_counts": {},
        "model_counts": {},
        "seed_count": 0,
        "step_summary": {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
        },
    }


def test_summarize_archive_runs_uses_archive_run_metadata(tmp_path: Path) -> None:
    dataset = _dataset_with_runs()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)

    summary = summarize_archive_runs(archive.path)

    assert summary["run_count"] == 3
    assert summary["completed_count"] == 2
    assert summary["failed_count"] == 1
    assert summary["status_counts"] == {"completed": 2, "failed": 1}
    assert summary["scenario_counts"] == {"baseline": 2, "policy": 1}
    assert summary["model_counts"] == {"ToyModel": 3}
    assert summary["seed_count"] == 3
    assert summary["step_summary"] == {
        "count": 3,
        "min": 3.0,
        "max": 10.0,
        "mean": 6.0,
    }


def test_experiment_archive_summarize_runs_method(tmp_path: Path) -> None:
    dataset = _dataset_with_runs()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)

    summary = archive.summarize_runs()

    assert summary["run_count"] == 3
    assert summary["status_counts"] == {"completed": 2, "failed": 1}
