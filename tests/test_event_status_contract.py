import pytest

from abmforge.core.model import Model
from abmforge.data.dataset import Dataset
from abmforge.data.schema import DatasetSchemaV1, SchemaValidationError
from abmforge.time.status import (
    CANCELLED,
    EXECUTED,
    FAILED,
    SCHEDULED,
    VALID_EVENT_STATUSES,
    validate_event_status,
)


def test_valid_event_statuses_are_explicit() -> None:
    assert {
        SCHEDULED,
        CANCELLED,
        EXECUTED,
        FAILED,
    } == VALID_EVENT_STATUSES


def test_validate_event_status_accepts_known_statuses() -> None:
    assert validate_event_status(SCHEDULED) == SCHEDULED
    assert validate_event_status(CANCELLED) == CANCELLED
    assert validate_event_status(EXECUTED) == EXECUTED
    assert validate_event_status(FAILED) == FAILED


def test_validate_event_status_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="Invalid event status"):
        validate_event_status("unknown")


def test_event_queue_records_scheduled_and_executed_statuses() -> None:
    model = Model()
    called = {"value": False}

    event = model.events.schedule(
        callback=lambda: called.__setitem__("value", True),
        after=1.0,
        owner="agent-1",
        tags=["test"],
    )

    assert model.record.dataset.event_records[-1]["event_id"] == event.event_id
    assert model.record.dataset.event_records[-1]["status"] == SCHEDULED

    executed = model.events.process_due(time=1.0)

    assert executed == 1
    assert called["value"] is True
    assert model.record.dataset.event_records[-1]["event_id"] == event.event_id
    assert model.record.dataset.event_records[-1]["status"] == EXECUTED


def test_event_queue_records_cancelled_status() -> None:
    model = Model()

    event = model.events.schedule(
        callback=lambda: None,
        after=1.0,
        owner="agent-1",
        tags=["test"],
    )

    assert model.events.cancel(event.event_id) is True
    assert model.record.dataset.event_records[-1]["event_id"] == event.event_id
    assert model.record.dataset.event_records[-1]["status"] == CANCELLED


def test_event_queue_records_failed_status() -> None:
    model = Model()

    def fail() -> None:
        raise RuntimeError("boom")

    event = model.events.schedule(
        callback=fail,
        after=1.0,
        owner="agent-1",
        tags=["test"],
    )

    with pytest.raises(RuntimeError, match="boom"):
        model.events.process_due(time=1.0)

    assert model.record.dataset.event_records[-1]["event_id"] == event.event_id
    assert model.record.dataset.event_records[-1]["status"] == FAILED


def _dataset_with_event_status(status: str) -> Dataset:
    dataset = Dataset(run_id="run-event-status-test")
    dataset.record_event(
        step=0,
        time=0.0,
        event_id=1,
        owner=None,
        tags=[],
        status=status,
    )
    return dataset


@pytest.mark.parametrize(
    "status",
    [
        SCHEDULED,
        CANCELLED,
        EXECUTED,
        FAILED,
    ],
)
def test_dataset_schema_accepts_known_event_statuses(status: str) -> None:
    dataset = _dataset_with_event_status(status)

    assert dataset.schema_errors() == []


def test_dataset_schema_rejects_unknown_event_status() -> None:
    dataset = _dataset_with_event_status("unknown")

    errors = dataset.schema_errors()

    assert any("event_records[0].status: expected one of" in error for error in errors)
    assert any("unknown" in error for error in errors)


def test_dataset_validate_raises_for_unknown_event_status() -> None:
    dataset = _dataset_with_event_status("unknown")

    with pytest.raises(SchemaValidationError, match=r"event_records\[0\]\.status"):
        dataset.validate()


def test_dataset_schema_exports_event_status_enum() -> None:
    schema = DatasetSchemaV1.to_dict()
    event_fields = schema["tables"]["event_records"]["fields"]

    status_fields = [field for field in event_fields if field["name"] == "status"]

    assert len(status_fields) == 1
    assert set(status_fields[0]["enum"]) == {
        SCHEDULED,
        CANCELLED,
        EXECUTED,
        FAILED,
    }
