from __future__ import annotations

import json

from abmforge import Model


def named_callback() -> None:
    return None


def test_event_queue_snapshot_metadata_records_pending_event_fields() -> None:
    model = Model(seed=123)
    model.time = 2.0

    event = model.events.schedule_after(
        3,
        callback=named_callback,
        owner="agent-1",
        tags=["audit", "demo"],
        priority=5,
    )

    metadata = model.events.snapshot_metadata()

    assert metadata["schema_version"] == "event-queue-metadata-v1"
    assert metadata["pending_count"] == 1
    assert metadata["cancelled_count"] == 0
    assert metadata["next_event_time"] == 5.0
    assert metadata["callback_restore_supported"] is False

    events = metadata["events"]
    assert len(events) == 1
    assert events[0]["event_id"] == event.event_id
    assert events[0]["time"] == 5.0
    assert events[0]["priority"] == 5
    assert events[0]["owner"] == "agent-1"
    assert events[0]["tags"] == ["audit", "demo"]
    assert events[0]["cancel_on_owner_removed"] is True
    assert events[0]["cancelled"] is False
    assert events[0]["callback"]["qualname"] == "named_callback"


def test_event_queue_snapshot_metadata_excludes_cancelled_by_default() -> None:
    model = Model(seed=123)

    event = model.events.schedule_after(1, callback=named_callback)
    model.events.cancel(event.event_id)

    metadata = model.events.snapshot_metadata()

    assert metadata["pending_count"] == 0
    assert metadata["cancelled_count"] == 1
    assert metadata["next_event_time"] is None
    assert metadata["events"] == []


def test_event_queue_snapshot_metadata_can_include_cancelled_events() -> None:
    model = Model(seed=123)

    event = model.events.schedule_after(1, callback=named_callback, tags=["cancelled"])
    model.events.cancel(event.event_id)

    metadata = model.events.snapshot_metadata(include_cancelled=True)

    assert metadata["pending_count"] == 0
    assert metadata["cancelled_count"] == 1
    assert metadata["next_event_time"] == 1.0
    assert metadata["events"][0]["event_id"] == event.event_id
    assert metadata["events"][0]["cancelled"] is True
    assert metadata["events"][0]["tags"] == ["cancelled"]


def test_model_snapshot_includes_event_queue_metadata() -> None:
    model = Model(seed=123)
    model.events.schedule_after(
        2,
        callback=named_callback,
        owner="agent-1",
        tags=["snapshot"],
    )

    snapshot = model.snapshot()

    assert "event_queue" in snapshot
    assert snapshot["event_queue"]["schema_version"] == "event-queue-metadata-v1"
    assert snapshot["event_queue"]["pending_count"] == 1
    assert snapshot["event_queue"]["callback_restore_supported"] is False

    json.dumps(snapshot["event_queue"])


def test_model_from_snapshot_does_not_restore_event_queue_callbacks() -> None:
    model = Model(seed=123)
    model.events.schedule_after(2, callback=named_callback)
    snapshot = model.snapshot()

    restored = Model.from_snapshot(snapshot)

    assert restored.events.pending_count() == 0
