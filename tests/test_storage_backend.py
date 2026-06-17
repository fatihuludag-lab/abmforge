from __future__ import annotations

from abmforge.data.dataset import Dataset
from abmforge.data.storage import InMemoryStorage, StorageBackend


def test_inmemory_storage_is_dataset():
    storage = InMemoryStorage(run_id="run-1")

    storage.record_model(
        step=1,
        time=1.0,
        metric="x",
        value=42,
    )

    assert isinstance(storage, Dataset)
    assert len(storage.model_records) == 1
    assert storage.model_records[0]["value"] == 42


def test_inmemory_storage_satisfies_protocol():
    storage: StorageBackend = InMemoryStorage(run_id="run-1")

    storage.add_run(run_id="run-1", status="running")
    storage.update_last_run(status="completed")

    assert isinstance(storage, InMemoryStorage)
