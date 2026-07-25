from __future__ import annotations

import pytest

from abmforge.data.schema import DatasetSchemaV1, SchemaValidationError
from abmforge.data.storage import ParquetStorage

pd = pytest.importorskip("pandas")
pytest.importorskip("pyarrow")


def test_parquet_storage_writes_tables(tmp_path):
    storage = ParquetStorage(run_id="run-1")

    storage.add_run(run_id="run-1", scenario="test", status="completed")
    storage.record_model(step=0, time=0.0, metric="count", value=1)
    storage.record_agent(
        step=0,
        time=0.0,
        agent_id=1,
        agent_type="TestAgent",
        variable="wealth",
        value=10,
    )
    storage.record_event(
        step=0,
        time=0.0,
        event_id="event-1",
        owner=None,
        tags=["test"],
        status="scheduled",
    )
    storage.record_lifecycle(
        step=0,
        time=0.0,
        event="created",
        agent_id=1,
        details={"source": "test"},
    )
    storage.record_error(
        step=0,
        time=0.0,
        exception_type="ValueError",
        message="test error",
        details={"x": 1},
    )

    output_dir = storage.write_parquet(tmp_path / "parquet")

    expected_files = [
        "runs.parquet",
        "model_records.parquet",
        "agent_records.parquet",
        "event_records.parquet",
        "lifecycle_records.parquet",
        "errors.parquet",
    ]

    for filename in expected_files:
        assert (output_dir / filename).exists()

    model_records = pd.read_parquet(output_dir / "model_records.parquet")
    assert model_records.loc[0, "metric"] == "count"
    assert model_records.loc[0, "value"] == 1


def test_parquet_storage_normalizes_nested_values(tmp_path):
    storage = ParquetStorage(run_id="run-1")

    storage.record_lifecycle(
        step=0,
        time=0.0,
        event="created",
        details={"nested": {"x": 1}},
    )

    output_dir = storage.write_parquet(tmp_path / "parquet")
    lifecycle_records = pd.read_parquet(output_dir / "lifecycle_records.parquet")

    assert isinstance(lifecycle_records.loc[0, "details"], str)
    assert '"nested"' in lifecycle_records.loc[0, "details"]


def test_parquet_storage_validates_before_writing(tmp_path) -> None:
    storage = ParquetStorage(run_id="run-1")
    storage.runs.append(
        {
            "status": "completed",
        }
    )

    output_dir = tmp_path / "parquet"

    with pytest.raises(
        SchemaValidationError,
        match=r"runs\[0\]\.run_id: missing required field",
    ):
        storage.write_parquet(output_dir)

    assert not output_dir.exists()


def test_parquet_storage_preserves_schema_columns_for_empty_tables(tmp_path) -> None:
    storage = ParquetStorage(run_id="empty-run")

    output_dir = storage.write_parquet(tmp_path / "parquet")

    for table_name, table_schema in DatasetSchemaV1.tables.items():
        frame = pd.read_parquet(output_dir / f"{table_name}.parquet")
        expected_columns = [field.name for field in table_schema.fields]

        assert list(frame.columns) == expected_columns
        assert frame.empty


def test_parquet_storage_preserves_schema_columns_before_extra_fields(
    tmp_path,
) -> None:
    storage = ParquetStorage(run_id="run-1")
    storage.add_run(
        run_id="run-1",
        scenario="custom",
        custom_metric="kept",
    )

    output_dir = storage.write_parquet(tmp_path / "parquet")
    frame = pd.read_parquet(output_dir / "runs.parquet")

    schema_columns = [field.name for field in DatasetSchemaV1.tables["runs"].fields]

    assert list(frame.columns[: len(schema_columns)]) == schema_columns
    assert "custom_metric" in frame.columns[len(schema_columns) :]
