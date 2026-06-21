from __future__ import annotations

from abmforge.data.dataset import Dataset
from abmforge.experiment.archive import ExperimentArchive


def make_dataset() -> Dataset:
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
    return dataset


def test_archive_validate_accepts_valid_parquet_outputs(tmp_path) -> None:
    dataset = make_dataset()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset, format="parquet")

    assert archive.validate() == []


def test_archive_validate_reports_corrupt_parquet_table(tmp_path) -> None:
    dataset = make_dataset()
    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="parquet")

    (archive.data_dir / "runs.parquet").write_bytes(b"not a parquet file")

    errors = archive.validate()

    assert any(
        error.startswith("Invalid parquet dataset table data/runs.parquet:") for error in errors
    )


def test_archive_validate_reports_missing_parquet_table(tmp_path) -> None:
    dataset = make_dataset()
    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="parquet")

    (archive.data_dir / "errors.parquet").unlink()

    errors = archive.validate()

    assert "Missing dataset table file: data/errors.parquet" in errors


def test_archive_validate_reports_parquet_record_count_mismatch(tmp_path) -> None:
    dataset = make_dataset()
    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="parquet")

    import pandas as pd

    pd.DataFrame(columns=["run_id", "step", "time", "metric", "value"]).to_parquet(
        archive.data_dir / "model_records.parquet", index=False
    )

    errors = archive.validate()

    assert "record_counts mismatch for model_records: manifest has 1, actual is 0" in errors
