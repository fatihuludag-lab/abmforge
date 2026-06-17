from __future__ import annotations

import pytest

from abmforge.data.dataset import Dataset
from abmforge.experiment.archive import ExperimentArchive

pytest.importorskip("pandas")


def test_experiment_archive_write_parquet_outputs(tmp_path):
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="parquet_scenario",
        model_name="TestModel",
        parameters={"x": 1},
        seed=42,
        status="completed",
    )
    dataset.record_model(step=0, time=0.0, metric="count", value=1)
    dataset.record_agent(
        step=0,
        time=0.0,
        agent_id=1,
        agent_type="TestAgent",
        variable="wealth",
        value=10,
    )
    dataset.record_event(
        step=0,
        time=0.0,
        event_id="event-1",
        owner=None,
        tags=["archive"],
        status="scheduled",
    )
    dataset.record_lifecycle(
        step=0,
        time=0.0,
        event="created",
        agent_id=1,
        details={"source": "archive-test"},
    )

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="parquet")

    expected_files = [
        "runs.parquet",
        "model_records.parquet",
        "agent_records.parquet",
        "event_records.parquet",
        "lifecycle_records.parquet",
        "errors.parquet",
    ]

    for filename in expected_files:
        assert (archive.data_dir / filename).exists()

    assert archive.manifest_path.exists()
    assert archive.dataset_schema_path.exists()
    assert archive.validate() == []


def test_experiment_archive_rejects_unknown_format(tmp_path):
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="bad_format",
        model_name="TestModel",
        parameters={},
        seed=1,
        status="completed",
    )

    archive = ExperimentArchive.create(tmp_path / "archive")

    with pytest.raises(ValueError, match="Unsupported archive format"):
        archive.write_run_outputs(dataset, format="unknown")  # type: ignore[arg-type]
