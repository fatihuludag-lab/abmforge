from __future__ import annotations

from collections.abc import Callable

import pytest

from abmforge.data.dataset import Dataset
from abmforge.data.storage import InMemoryStorage, ParquetStorage, StorageBackend

StorageFactory = Callable[[str], Dataset]


@pytest.fixture(
    params=[
        InMemoryStorage,
        ParquetStorage,
    ],
    ids=[
        "inmemory",
        "parquet",
    ],
)
def storage(request: pytest.FixtureRequest) -> Dataset:
    factory: StorageFactory = request.param
    return factory("run-1")


def test_storage_backend_is_dataset(storage: Dataset) -> None:
    assert isinstance(storage, Dataset)
    assert storage.run_id == "run-1"


def test_storage_backend_exposes_expected_dataset_tables(storage: Dataset) -> None:
    assert storage.runs == []
    assert storage.model_records == []
    assert storage.agent_records == []
    assert storage.event_records == []
    assert storage.lifecycle_records == []
    assert storage.errors == []


def test_storage_backend_records_all_table_types(storage: Dataset) -> None:
    storage.add_run(run_id="run-1", status="running")
    storage.update_last_run(status="completed")
    storage.record_model(
        step=1,
        time=1.0,
        metric="x",
        value=42,
    )
    storage.record_agent(
        step=1,
        time=1.0,
        agent_id=1,
        agent_type="Person",
        variable="wealth",
        value=42,
    )
    storage.record_event(
        step=1,
        time=1.0,
        event_id="event-1",
        owner=1,
        tags=["test"],
        status="scheduled",
    )
    storage.record_lifecycle(
        step=1,
        time=1.0,
        event="agent_created",
        agent_id=1,
        details={"agent_type": "Person"},
    )
    storage.record_error(
        step=1,
        time=1.0,
        exception_type="ValueError",
        message="example",
    )

    assert storage.runs[-1]["status"] == "completed"
    assert storage.model_records[-1]["value"] == 42
    assert storage.agent_records[-1]["agent_id"] == 1
    assert storage.event_records[-1]["event_id"] == "event-1"
    assert storage.lifecycle_records[-1]["event"] == "agent_created"
    assert storage.errors[-1]["exception_type"] == "ValueError"


def test_storage_backend_produces_valid_dataset(storage: Dataset) -> None:
    storage.add_run(run_id="run-1", status="completed")
    storage.record_model(
        step=0,
        time=0.0,
        metric="count",
        value=1,
    )

    storage.validate()

    assert storage.schema_errors() == []


def test_storage_backend_to_dict_uses_canonical_tables(storage: Dataset) -> None:
    assert tuple(storage.to_dict()) == (
        "runs",
        "model_records",
        "agent_records",
        "event_records",
        "lifecycle_records",
        "errors",
    )


def test_storage_protocol_accepts_supported_backends() -> None:
    inmemory: StorageBackend = InMemoryStorage(run_id="run-1")
    parquet: StorageBackend = ParquetStorage(run_id="run-2")

    assert inmemory.run_id == "run-1"
    assert parquet.run_id == "run-2"
