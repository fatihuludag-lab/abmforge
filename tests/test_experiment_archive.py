from __future__ import annotations

from abmforge.data.dataset import Dataset
from abmforge.experiment.archive import ExperimentArchive


def test_experiment_archive_create(tmp_path):
    archive = ExperimentArchive.create(tmp_path / "archive")

    assert archive.path.exists()
    assert archive.data_dir.exists()
    assert archive.snapshots_dir.exists()
    assert archive.reports_dir.exists()
    assert archive.logs_dir.exists()


def test_experiment_archive_write_minimum_outputs(tmp_path):
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="test_scenario",
        model_name="TestModel",
        parameters={"x": 1},
        seed=42,
        status="completed",
    )
    dataset.record_model(step=0, time=0.0, metric="count", value=1)

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset)

    assert archive.manifest_path.exists()
    assert archive.dataset_schema_path.exists()
    assert (archive.data_dir / "runs.json").exists()
    assert (archive.data_dir / "model_records.jsonl").exists()
    assert archive.validate() == []


def test_experiment_archive_validate_reports_missing_files(tmp_path):
    archive = ExperimentArchive.create(tmp_path / "archive")

    errors = archive.validate()

    assert "Missing manifest.json" in errors
    assert "Missing dataset_schema.json" in errors
    assert "Data directory is empty" in errors
