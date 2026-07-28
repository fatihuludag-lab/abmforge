from __future__ import annotations

import sys

import pytest

from abmforge.data import (
    ExperimentDataset,
    ExperimentDatasetDependencyError,
    ExperimentDatasetError,
    ExperimentDatasetQueryError,
    ExperimentDatasetTableError,
    ExperimentDatasetTableNotFoundError,
)
from abmforge.data.dataset import Dataset
from abmforge.experiment.archive import ExperimentArchive

pd = pytest.importorskip("pandas")
pytest.importorskip("duckdb")


def test_experiment_dataset_opens_archive_root_and_queries_parquet(tmp_path):
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="query_scenario",
        model_name="TestModel",
        parameters={"x": 1},
        seed=42,
        status="completed",
    )
    dataset.record_model(step=0, time=0.0, metric="count", value=1)
    dataset.record_model(step=1, time=1.0, metric="count", value=3)

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="parquet")

    experiment_dataset = ExperimentDataset.open(archive.path)

    assert "model_records" in experiment_dataset.available_tables()

    result = experiment_dataset.query(
        """
        SELECT
            metric,
            SUM(value) AS total_value
        FROM model_records
        GROUP BY metric
        """
    )

    assert result.loc[0, "metric"] == "count"
    assert result.loc[0, "total_value"] == 4


def test_experiment_dataset_opens_data_dir(tmp_path):
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="query_scenario",
        model_name="TestModel",
        parameters={},
        seed=1,
        status="completed",
    )
    dataset.record_model(step=0, time=0.0, metric="x", value=5)

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="parquet")

    experiment_dataset = ExperimentDataset.open(archive.data_dir)

    result = experiment_dataset.query("SELECT COUNT(*) AS n FROM model_records")

    assert result.loc[0, "n"] == 1


def test_experiment_dataset_requires_existing_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        ExperimentDataset.open(tmp_path / "missing")


def test_experiment_dataset_reports_missing_required_tables(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    experiment_dataset = ExperimentDataset.open(data_dir)

    with pytest.raises(FileNotFoundError, match="model_records"):
        experiment_dataset.require_tables(["model_records"])


def test_experiment_dataset_reports_corrupt_parquet_table(
    tmp_path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    parquet_path = data_dir / "model_records.parquet"
    parquet_path.write_bytes(b"not-a-valid-parquet-file")

    experiment_dataset = ExperimentDataset.open(data_dir)

    with pytest.raises(
        ExperimentDatasetTableError,
        match="model_records.*could not be read",
    ):
        experiment_dataset.query("SELECT * FROM model_records")


def test_experiment_dataset_wraps_sql_query_errors(
    tmp_path,
) -> None:
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="query_scenario",
        model_name="TestModel",
        parameters={},
        seed=1,
        status="completed",
    )

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="parquet")

    experiment_dataset = ExperimentDataset.open(archive.path)

    with pytest.raises(
        ExperimentDatasetQueryError,
        match="SQL query failed",
    ):
        experiment_dataset.query("SELECT * FROM table_that_does_not_exist")


def test_experiment_dataset_reports_missing_duckdb_dependency(
    tmp_path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    experiment_dataset = ExperimentDataset.open(data_dir)
    monkeypatch.setitem(sys.modules, "duckdb", None)

    with pytest.raises(
        ExperimentDatasetDependencyError,
        match=r"pip install abmforge\[data\]",
    ):
        experiment_dataset.query("SELECT 1")


def test_experiment_dataset_uses_specific_missing_table_error(
    tmp_path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    experiment_dataset = ExperimentDataset.open(data_dir)

    with pytest.raises(
        ExperimentDatasetTableNotFoundError,
        match="model_records",
    ):
        experiment_dataset.require_tables(["model_records"])


def test_missing_table_error_preserves_both_error_contracts(tmp_path):
    dataset = ExperimentDataset.open(tmp_path)

    with pytest.raises(ExperimentDatasetError) as exc_info:
        dataset.require_tables(["model_records"])

    assert isinstance(exc_info.value, FileNotFoundError)
