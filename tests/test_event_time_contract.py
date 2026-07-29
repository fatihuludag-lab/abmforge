from __future__ import annotations

from typing import Any

import pytest

from abmforge import Model


class _FloatConvertible:
    """Object that must not be accepted through implicit float coercion."""

    def __float__(self) -> float:
        return 1.0


@pytest.mark.parametrize(
    "event_time",
    [
        0.5,
        1.25,
    ],
)
def test_schedule_at_rejects_fractional_time(
    event_time: float,
) -> None:
    model = Model(seed=42)

    with pytest.raises(
        ValueError,
        match="event time must be an integer tick",
    ):
        model.events.schedule_at(
            event_time,
            callback=lambda: None,
        )


@pytest.mark.parametrize(
    "delay",
    [
        0.5,
        1.25,
    ],
)
def test_schedule_after_rejects_fractional_delay(
    delay: float,
) -> None:
    model = Model(seed=42)

    with pytest.raises(
        ValueError,
        match="after must be an integer tick",
    ):
        model.events.schedule_after(
            delay,
            callback=lambda: None,
        )


@pytest.mark.parametrize(
    "invalid_time",
    [
        True,
        False,
        "1",
        _FloatConvertible(),
    ],
)
def test_schedule_at_rejects_implicit_numeric_coercion(
    invalid_time: Any,
) -> None:
    model = Model(seed=42)

    with pytest.raises(
        TypeError,
        match="event time must be a real number",
    ):
        model.events.schedule_at(
            invalid_time,
            callback=lambda: None,
        )


@pytest.mark.parametrize(
    "invalid_delay",
    [
        True,
        False,
        "1",
        _FloatConvertible(),
    ],
)
def test_schedule_after_rejects_implicit_numeric_coercion(
    invalid_delay: Any,
) -> None:
    model = Model(seed=42)

    with pytest.raises(
        TypeError,
        match="after must be a real number",
    ):
        model.events.schedule_after(
            invalid_delay,
            callback=lambda: None,
        )


def test_schedule_at_accepts_integer_valued_float() -> None:
    model = Model(seed=42)
    executions: list[float] = []

    event = model.events.schedule_at(
        1.0,
        callback=lambda: executions.append(model.time),
    )

    model.run_for(2)

    assert event.time == 1.0
    assert executions == [1.0]


def test_schedule_after_accepts_integer_valued_float() -> None:
    model = Model(seed=42)
    executions: list[float] = []

    event = model.events.schedule_after(
        1.0,
        callback=lambda: executions.append(model.time),
    )

    model.run_for(2)

    assert event.time == 1.0
    assert executions == [1.0]


def test_direct_schedule_rejects_fractional_at() -> None:
    model = Model(seed=42)

    with pytest.raises(
        ValueError,
        match="event time must be an integer tick",
    ):
        model.events.schedule(
            at=0.5,
            callback=lambda: None,
        )


def test_direct_schedule_rejects_fractional_after() -> None:
    model = Model(seed=42)

    with pytest.raises(
        ValueError,
        match="after must be an integer tick",
    ):
        model.events.schedule(
            after=0.5,
            callback=lambda: None,
        )


def test_rejected_absolute_time_does_not_mutate_event_queue() -> None:
    model = Model(seed=42)

    with pytest.raises(
        ValueError,
        match="event time must be an integer tick",
    ):
        model.events.schedule_at(
            0.5,
            callback=lambda: None,
        )

    assert model.events.pending_count() == 0
    assert model.events.next_event_time() is None
    assert model.record.dataset.event_records == []

    accepted = model.events.schedule_at(
        1,
        callback=lambda: None,
    )

    assert accepted.event_id == 1


def test_rejected_delay_does_not_mutate_event_queue() -> None:
    model = Model(seed=42)

    with pytest.raises(
        TypeError,
        match="after must be a real number",
    ):
        model.events.schedule_after(
            True,
            callback=lambda: None,
        )

    assert model.events.pending_count() == 0
    assert model.events.next_event_time() is None
    assert model.record.dataset.event_records == []

    accepted = model.events.schedule_after(
        1,
        callback=lambda: None,
    )

    assert accepted.event_id == 1


@pytest.mark.parametrize(
    "event_time",
    [
        0,
        1,
        2.0,
    ],
)
def test_schedule_at_accepts_non_negative_integer_ticks(
    event_time: int | float,
) -> None:
    model = Model(seed=42)

    event = model.events.schedule_at(
        event_time,
        callback=lambda: None,
    )

    assert event.time == float(event_time)


@pytest.mark.parametrize(
    "delay",
    [
        0,
        1,
        2.0,
    ],
)
def test_schedule_after_accepts_non_negative_integer_delays(
    delay: int | float,
) -> None:
    model = Model(seed=42)

    event = model.events.schedule_after(
        delay,
        callback=lambda: None,
    )

    assert event.time == float(delay)


@pytest.mark.parametrize(
    ("method_name", "error_message"),
    [
        ("schedule_at", "event time must be finite"),
        ("schedule_after", "after must be finite"),
    ],
)
def test_schedule_rejects_unrepresentably_large_integer(
    method_name: str,
    error_message: str,
) -> None:
    model = Model(seed=42)
    method = getattr(model.events, method_name)

    with pytest.raises(
        ValueError,
        match=error_message,
    ):
        method(
            10**400,
            callback=lambda: None,
        )

    assert model.events.pending_count() == 0
    assert model.record.dataset.event_records == []
