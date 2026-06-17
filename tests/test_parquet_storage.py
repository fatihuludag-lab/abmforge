from __future__ import annotations

import pytest

from abmforge.data.storage import ParquetStorage

pd = pytest.importorskip("pandas")


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
