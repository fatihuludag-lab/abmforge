from __future__ import annotations

import pytest

from abmforge import Agent, Model


class Person(Agent):
    pass


def test_schedule_and_execute_event() -> None:
    model = Model(seed=1)
    model.hit = 0

    def callback() -> None:
        model.hit += 1

    model.events.schedule(after=0, callback=callback, tags=["test"])
    executed = model.events.process_due(time=0)

    assert executed == 1
    assert model.hit == 1
    assert model.record.dataset.event_records[-1]["status"] == "executed"


def test_cancel_event() -> None:
    model = Model(seed=1)
    model.hit = 0

    def callback() -> None:
        model.hit += 1

    event = model.events.schedule(after=0, callback=callback)
    assert model.events.cancel(event.event_id) is True
    executed = model.events.process_due(time=0)

    assert executed == 0
    assert model.hit == 0


def test_cancel_by_owner_when_agent_removed() -> None:
    model = Model(seed=1)
    agent = model.agents.create(Person)[0]
    model.hit = 0

    def callback() -> None:
        model.hit += 1

    model.events.schedule(after=1, callback=callback, owner=agent.unique_id, tags=["owned"])
    assert model.events.pending_count() == 1

    model.remove_agent(agent)

    assert model.events.pending_count() == 0
    model.events.process_due(time=1)
    assert model.hit == 0


def test_schedule_after_and_schedule_at_helpers_execute_in_time_order() -> None:
    model = Model(seed=1)
    model.time = 5.0
    model.hit = []

    model.events.schedule_after(2, callback=lambda: model.hit.append("after"))
    model.events.schedule_at(6, callback=lambda: model.hit.append("at"))

    assert model.events.next_event_time() == 6.0
    assert model.events.process_due(time=6) == 1
    assert model.hit == ["at"]
    assert model.events.process_due(time=7) == 1
    assert model.hit == ["at", "after"]


def test_pending_events_are_sorted_and_filterable() -> None:
    model = Model(seed=1)

    third = model.events.schedule_after(
        3,
        callback=lambda: None,
        owner="b",
        tags=["late"],
    )
    first = model.events.schedule_after(
        1,
        callback=lambda: None,
        owner="a",
        tags=["early", "shared"],
    )
    second = model.events.schedule_after(
        2,
        callback=lambda: None,
        owner="a",
        tags=["shared"],
    )

    assert model.events.has_pending() is True
    assert model.events.pending_events() == [first, second, third]
    assert model.events.pending_events(owner="a") == [first, second]
    assert model.events.pending_events(tag="shared") == [first, second]
    assert model.events.next_event_time() == 1.0


def test_pending_event_inspection_ignores_cancelled_events() -> None:
    model = Model(seed=1)

    event = model.events.schedule_after(1, callback=lambda: None)
    assert model.events.has_pending() is True

    assert model.events.cancel(event.event_id) is True

    assert model.events.pending_events() == []
    assert model.events.next_event_time() is None
    assert model.events.has_pending() is False
    assert model.events.pending_count() == 0


def test_schedule_after_rejects_negative_delay() -> None:
    model = Model(seed=1)

    with pytest.raises(ValueError, match="after must be non-negative"):
        model.events.schedule_after(-1, callback=lambda: None)


def test_schedule_at_rejects_past_time() -> None:
    model = Model(seed=1)
    model.time = 10

    with pytest.raises(ValueError, match="cannot schedule an event in the past"):
        model.events.schedule_at(9, callback=lambda: None)


@pytest.mark.parametrize(
    "invalid_time",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_schedule_at_rejects_non_finite_time(invalid_time: float) -> None:
    model = Model(seed=1)

    with pytest.raises(ValueError, match="event time must be finite"):
        model.events.schedule_at(invalid_time, callback=lambda: None)


@pytest.mark.parametrize(
    "invalid_delay",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_schedule_after_rejects_non_finite_delay(invalid_delay: float) -> None:
    model = Model(seed=1)

    with pytest.raises(ValueError, match="after must be finite"):
        model.events.schedule_after(invalid_delay, callback=lambda: None)


def test_schedule_rejects_non_callable_callback() -> None:
    model = Model(seed=1)

    with pytest.raises(TypeError, match="callback must be callable"):
        model.events.schedule_after(1, callback=42)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "invalid_priority",
    [
        1.5,
        "high",
        None,
        True,
    ],
)
def test_schedule_rejects_non_integer_priority(invalid_priority: object) -> None:
    model = Model(seed=1)

    with pytest.raises(TypeError, match="priority must be an integer"):
        model.events.schedule_after(
            1,
            callback=lambda: None,
            priority=invalid_priority,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "invalid_tags",
    [
        ["valid", 1],
        [None],
        [object()],
    ],
)
def test_schedule_rejects_non_string_tags(invalid_tags: list[object]) -> None:
    model = Model(seed=1)

    with pytest.raises(TypeError, match="tags must contain only strings"):
        model.events.schedule_after(
            1,
            callback=lambda: None,
            tags=invalid_tags,  # type: ignore[arg-type]
        )


def test_callback_can_schedule_same_time_event_deterministically() -> None:
    model = Model(seed=1)
    execution_order: list[str] = []

    def first_callback() -> None:
        execution_order.append("first")
        model.events.schedule_at(
            0,
            callback=lambda: execution_order.append("scheduled-during-callback"),
        )

    model.events.schedule_at(0, callback=first_callback)
    model.events.schedule_at(
        0,
        callback=lambda: execution_order.append("already-pending"),
    )

    executed = model.events.process_due(time=0)

    assert executed == 3
    assert execution_order == [
        "first",
        "already-pending",
        "scheduled-during-callback",
    ]
    assert model.events.pending_count() == 0


def test_callback_failure_preserves_other_due_events() -> None:
    model = Model(seed=1)
    execution_order: list[str] = []

    def failing_callback() -> None:
        execution_order.append("failed")
        raise RuntimeError("boom")

    model.events.schedule_at(0, callback=failing_callback)
    model.events.schedule_at(
        0,
        callback=lambda: execution_order.append("remaining"),
    )

    with pytest.raises(RuntimeError, match="boom"):
        model.events.process_due(time=0)

    assert execution_order == ["failed"]
    assert model.events.pending_count() == 1

    assert model.events.process_due(time=0) == 1
    assert execution_order == ["failed", "remaining"]
