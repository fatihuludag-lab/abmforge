from pathlib import Path

from abmforge.data.dataset import Dataset
from abmforge.experiment import (
    ExperimentArchive,
    summarize_archive_runs,
    summarize_archive_runs_by,
    summarize_run_records,
    summarize_run_records_by,
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


def test_summarize_run_records_by_single_field() -> None:
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
            "status": "failed",
            "steps": 1,
        },
        {
            "run_id": "run-003",
            "scenario": "policy",
            "model_name": "ToyModel",
            "seed": 3,
            "status": "completed",
            "steps": 10,
        },
    ]

    summary = summarize_run_records_by(records, by="scenario")

    assert summary["group_by"] == ["scenario"]
    assert summary["group_count"] == 2
    assert summary["groups"] == [
        {
            "key": {"scenario": "baseline"},
            "summary": {
                "run_count": 2,
                "completed_count": 1,
                "failed_count": 1,
                "status_counts": {"completed": 1, "failed": 1},
                "scenario_counts": {"baseline": 2},
                "model_counts": {"ToyModel": 2},
                "seed_count": 2,
                "step_summary": {
                    "count": 2,
                    "min": 1.0,
                    "max": 5.0,
                    "mean": 3.0,
                },
            },
        },
        {
            "key": {"scenario": "policy"},
            "summary": {
                "run_count": 1,
                "completed_count": 1,
                "failed_count": 0,
                "status_counts": {"completed": 1},
                "scenario_counts": {"policy": 1},
                "model_counts": {"ToyModel": 1},
                "seed_count": 1,
                "step_summary": {
                    "count": 1,
                    "min": 10.0,
                    "max": 10.0,
                    "mean": 10.0,
                },
            },
        },
    ]


def test_summarize_run_records_by_multiple_fields() -> None:
    records = [
        {
            "run_id": "run-001",
            "scenario": "baseline",
            "status": "completed",
            "steps": 5,
        },
        {
            "run_id": "run-002",
            "scenario": "baseline",
            "status": "failed",
            "steps": 1,
        },
        {
            "run_id": "run-003",
            "scenario": "policy",
            "status": "completed",
            "steps": 10,
        },
    ]

    summary = summarize_run_records_by(records, by=["scenario", "status"])

    assert summary["group_by"] == ["scenario", "status"]
    assert summary["group_count"] == 3
    assert [group["key"] for group in summary["groups"]] == [
        {"scenario": "baseline", "status": "completed"},
        {"scenario": "baseline", "status": "failed"},
        {"scenario": "policy", "status": "completed"},
    ]


def test_summarize_run_records_by_missing_values() -> None:
    records = [
        {
            "run_id": "run-001",
            "scenario": "baseline",
            "status": "completed",
            "steps": 5,
        },
        {
            "run_id": "run-002",
            "status": "completed",
            "steps": 10,
        },
    ]

    summary = summarize_run_records_by(records, by="scenario")

    assert [group["key"] for group in summary["groups"]] == [
        {"scenario": "<missing>"},
        {"scenario": "baseline"},
    ]


def test_summarize_run_records_by_rejects_invalid_group_fields() -> None:
    records = [
        {
            "run_id": "run-001",
            "scenario": "baseline",
            "status": "completed",
        }
    ]

    try:
        summarize_run_records_by(records, by=[])
    except ValueError as exc:
        assert "by must contain at least one field" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

    try:
        summarize_run_records_by(records, by="")
    except ValueError as exc:
        assert "group fields must be non-empty strings" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

    try:
        summarize_run_records_by(records, by=["scenario", 1])  # type: ignore[list-item]
    except TypeError as exc:
        assert "group fields must be strings" in str(exc)
    else:
        raise AssertionError("Expected TypeError")


def test_summarize_archive_runs_by_uses_archive_run_metadata(tmp_path: Path) -> None:
    dataset = _dataset_with_runs()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)

    summary = summarize_archive_runs_by(archive.path, by="scenario")

    assert summary["group_by"] == ["scenario"]
    assert summary["group_count"] == 2
    assert [group["key"] for group in summary["groups"]] == [
        {"scenario": "baseline"},
        {"scenario": "policy"},
    ]


def test_experiment_archive_summarize_runs_by_method(tmp_path: Path) -> None:
    dataset = _dataset_with_runs()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)

    summary = archive.summarize_runs_by(["scenario", "status"])

    assert summary["group_by"] == ["scenario", "status"]
    assert summary["group_count"] == 2
