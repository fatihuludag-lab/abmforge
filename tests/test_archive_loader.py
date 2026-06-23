import json
from pathlib import Path
from typing import Any

from abmforge.data.dataset import Dataset
from abmforge.experiment import (
    ExperimentArchive,
    load_archive_run_records,
    load_archive_runs,
)


def _dataset_with_run() -> Dataset:
    dataset = Dataset(run_id="run-001")
    dataset.add_run(
        run_id="run-001",
        scenario="baseline",
        model_name="ToyModel",
        parameters={"alpha": 0.2},
        seed=42,
        status="completed",
        started_at="2026-06-22T10:00:00+00:00",
        ended_at="2026-06-22T10:00:01+00:00",
        steps=5,
        stop_reason=None,
    )
    return dataset


def _records_from_frame_or_list(value: Any) -> list[dict[str, Any]]:
    if hasattr(value, "to_dict"):
        records = value.to_dict("records")
        return [dict(record) for record in records]
    return [dict(record) for record in value]


def test_load_archive_run_records_prefers_run_index(tmp_path: Path) -> None:
    dataset = _dataset_with_run()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)

    records = load_archive_run_records(archive.path)

    assert len(records) == 1
    assert records[0]["run_id"] == "run-001"
    assert records[0]["scenario"] == "baseline"
    assert records[0]["model_name"] == "ToyModel"
    assert records[0]["seed"] == 42
    assert records[0]["status"] == "completed"
    assert records[0]["steps"] == 5
    assert records[0]["parameters"] == {"alpha": 0.2}
    assert records[0]["archive_path"] == "."
    assert records[0]["dataset_path"] == "data"
    assert records[0]["manifest_path"] == "manifest.json"
    assert records[0]["dataset_schema_path"] == "dataset_schema.json"


def test_load_archive_runs_returns_dataframe_when_pandas_is_available_or_list(
    tmp_path: Path,
) -> None:
    dataset = _dataset_with_run()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)

    runs = load_archive_runs(archive.path)
    records = _records_from_frame_or_list(runs)

    assert records[0]["run_id"] == "run-001"
    assert records[0]["scenario"] == "baseline"
    assert records[0]["model_name"] == "ToyModel"
    assert records[0]["seed"] == 42


def test_experiment_archive_load_runs_method(tmp_path: Path) -> None:
    dataset = _dataset_with_run()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)

    runs = archive.load_runs()
    records = _records_from_frame_or_list(runs)

    assert records[0]["run_id"] == "run-001"
    assert records[0]["status"] == "completed"


def test_load_archive_run_records_falls_back_to_legacy_runs_json(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "legacy_archive"
    data_dir = archive_path / "data"
    data_dir.mkdir(parents=True)

    (data_dir / "runs.json").write_text(
        json.dumps(
            [
                {
                    "run_id": "legacy-run",
                    "scenario": "legacy",
                    "model_name": "LegacyModel",
                    "seed": 7,
                    "status": "completed",
                    "steps": 3,
                }
            ]
        ),
        encoding="utf-8",
    )

    records = load_archive_run_records(archive_path)

    assert records == [
        {
            "run_id": "legacy-run",
            "scenario": "legacy",
            "model_name": "LegacyModel",
            "seed": 7,
            "status": "completed",
            "steps": 3,
        }
    ]


def test_load_archive_run_records_rejects_invalid_legacy_runs_json(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "legacy_archive"
    data_dir = archive_path / "data"
    data_dir.mkdir(parents=True)

    (data_dir / "runs.json").write_text(
        json.dumps({"run_id": "not-a-list"}),
        encoding="utf-8",
    )

    try:
        load_archive_run_records(archive_path)
    except ValueError as exc:
        assert "data/runs.json must contain a JSON array" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_load_archive_run_records_reports_missing_metadata(tmp_path: Path) -> None:
    archive_path = tmp_path / "empty_archive"
    archive_path.mkdir()

    try:
        load_archive_run_records(archive_path)
    except FileNotFoundError as exc:
        assert "Expected run_index.json or data/runs.json" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")
