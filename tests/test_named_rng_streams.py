from __future__ import annotations

from copy import deepcopy
from typing import Any

import numpy as np
import pytest
from numpy.random import Generator

from abmforge import Agent, Model, read_snapshot, write_snapshot
from abmforge.scheduling import RandomActivation, StagedActivation

_STREAM_POLICY = "named-rng-streams-v1"


def _draw(generator: Generator, count: int = 8) -> list[float]:
    return [float(value) for value in generator.random(count)]


class _RandomActivationAgent(Agent):
    def __init__(
        self,
        model: Model,
        unique_id: int,
        *,
        behavior_draws: int,
        activation_log: list[int],
    ) -> None:
        super().__init__(
            model=model,
            unique_id=unique_id,
        )
        self.behavior_draws = behavior_draws
        self.activation_log = activation_log

    def step(self) -> None:
        self.activation_log.append(int(self.unique_id))

        self.rng.random(self.behavior_draws)


class _StagedActivationAgent(Agent):
    def __init__(
        self,
        model: Model,
        unique_id: int,
        *,
        behavior_draws: int,
        activation_log: list[int],
    ) -> None:
        super().__init__(
            model=model,
            unique_id=unique_id,
        )
        self.behavior_draws = behavior_draws
        self.activation_log = activation_log

    def act(self) -> None:
        self.activation_log.append(int(self.unique_id))

        self.rng.random(self.behavior_draws)


def _random_activation_orders(
    *,
    behavior_draws: int,
) -> list[list[int]]:
    model = Model(seed=20260730)
    flat_log: list[int] = []

    for unique_id in range(10):
        model.agents.add(
            _RandomActivationAgent(
                model,
                unique_id,
                behavior_draws=behavior_draws,
                activation_log=flat_log,
            )
        )

    scheduler = RandomActivation(model)
    orders: list[list[int]] = []

    for _ in range(5):
        start = len(flat_log)
        scheduler.step()
        orders.append(flat_log[start:].copy())

    return orders


def _staged_activation_orders(
    *,
    behavior_draws: int,
) -> list[list[int]]:
    model = Model(seed=20260730)
    flat_log: list[int] = []

    for unique_id in range(10):
        model.agents.add(
            _StagedActivationAgent(
                model,
                unique_id,
                behavior_draws=behavior_draws,
                activation_log=flat_log,
            )
        )

    scheduler = StagedActivation(
        model,
        stages=["act"],
        shuffle=True,
    )
    orders: list[list[int]] = []

    for _ in range(5):
        start = len(flat_log)
        scheduler.step()
        orders.append(flat_log[start:].copy())

    return orders


def _collection_shuffle_orders(
    *,
    behavior_draws: int,
) -> list[list[int]]:
    model = Model(seed=20260730)
    flat_log: list[int] = []

    for unique_id in range(10):
        model.agents.add(
            _RandomActivationAgent(
                model,
                unique_id,
                behavior_draws=behavior_draws,
                activation_log=flat_log,
            )
        )

    orders: list[list[int]] = []

    for _ in range(5):
        start = len(flat_log)
        model.agents.shuffle_do("step")
        orders.append(flat_log[start:].copy())

    return orders


def test_same_named_stream_returns_same_generator_object() -> None:
    model = Model(seed=42)

    first = model.rng_stream("scheduler")
    second = model.rng_stream("scheduler")

    assert first is second


def test_same_seed_and_stream_name_are_reproducible() -> None:
    first = Model(seed=42)
    second = Model(seed=42)

    assert _draw(first.rng_stream("scheduler")) == _draw(second.rng_stream("scheduler"))


def test_stream_creation_order_does_not_change_draws() -> None:
    first = Model(seed=42)

    first_scheduler = _draw(first.rng_stream("scheduler"))
    first_events = _draw(first.rng_stream("events"))

    second = Model(seed=42)

    second_events = _draw(second.rng_stream("events"))
    second_scheduler = _draw(second.rng_stream("scheduler"))

    assert first_scheduler == second_scheduler
    assert first_events == second_events


def test_different_stream_names_produce_different_draws() -> None:
    model = Model(seed=42)

    scheduler_draws = _draw(model.rng_stream("scheduler"))
    event_draws = _draw(model.rng_stream("events"))

    assert scheduler_draws != event_draws


def test_accessing_named_stream_does_not_consume_default_rng() -> None:
    model = Model(seed=42)
    expected = np.random.default_rng(42)

    model.rng_stream("scheduler").random(100)

    np.testing.assert_array_equal(
        model.rng.random(10),
        expected.random(10),
    )


@pytest.mark.parametrize(
    ("name", "error_type"),
    [
        (None, TypeError),
        (1, TypeError),
        (b"scheduler", TypeError),
        ("", ValueError),
        ("   ", ValueError),
    ],
)
def test_invalid_stream_names_are_rejected(
    name: Any,
    error_type: type[Exception],
) -> None:
    model = Model(seed=42)

    with pytest.raises(
        error_type,
        match="stream name",
    ):
        model.rng_stream(name)


def test_random_activation_isolated_from_agent_behavior_rng() -> None:
    without_behavior_draws = _random_activation_orders(
        behavior_draws=0,
    )
    with_behavior_draws = _random_activation_orders(
        behavior_draws=7,
    )

    assert without_behavior_draws == with_behavior_draws


def test_collection_shuffle_isolated_from_agent_behavior_rng() -> None:
    without_behavior_draws = _collection_shuffle_orders(
        behavior_draws=0,
    )
    with_behavior_draws = _collection_shuffle_orders(
        behavior_draws=7,
    )

    assert without_behavior_draws == with_behavior_draws


def test_staged_shuffle_isolated_from_agent_behavior_rng() -> None:
    without_behavior_draws = _staged_activation_orders(
        behavior_draws=0,
    )
    with_behavior_draws = _staged_activation_orders(
        behavior_draws=7,
    )

    assert without_behavior_draws == with_behavior_draws


def test_snapshot_records_named_stream_policy_and_states() -> None:
    model = Model(seed=42)

    model.rng_stream("scheduler").random(5)
    model.rng_stream("events").random(3)

    snapshot = model.snapshot()

    assert snapshot["rng_stream_policy"] == _STREAM_POLICY
    assert isinstance(
        snapshot["rng_stream_root"],
        str,
    )
    assert len(snapshot["rng_stream_root"]) == 64

    stream_states = snapshot["rng_streams"]

    assert set(stream_states) == {
        "events",
        "scheduler",
    }
    assert isinstance(
        stream_states["scheduler"],
        dict,
    )
    assert isinstance(
        stream_states["events"],
        dict,
    )


def test_snapshot_restore_continues_opened_named_streams() -> None:
    model = Model(seed=42)

    scheduler_rng = model.rng_stream("scheduler")
    event_rng = model.rng_stream("events")

    scheduler_rng.random(11)
    event_rng.random(7)
    model.rng.random(5)

    snapshot = model.snapshot()

    expected_default = _draw(model.rng)
    expected_scheduler = _draw(scheduler_rng)
    expected_events = _draw(event_rng)

    restored = Model.from_snapshot(snapshot)

    assert _draw(restored.rng) == expected_default
    assert _draw(restored.rng_stream("scheduler")) == expected_scheduler
    assert _draw(restored.rng_stream("events")) == expected_events


@pytest.mark.parametrize(
    "seed",
    [
        42,
        None,
    ],
)
def test_snapshot_restore_preserves_unopened_stream_derivation(
    seed: int | None,
) -> None:
    model = Model(seed=seed)
    snapshot = model.snapshot()

    expected = _draw(model.rng_stream("future-component"))

    restored = Model.from_snapshot(snapshot)

    assert _draw(restored.rng_stream("future-component")) == expected


def test_legacy_snapshot_without_named_stream_fields_still_restores() -> None:
    model = Model(seed=42)
    model.rng.random(7)

    snapshot = model.snapshot()
    snapshot.pop(
        "rng_stream_policy",
        None,
    )
    snapshot.pop(
        "rng_stream_root",
        None,
    )
    snapshot.pop(
        "rng_streams",
        None,
    )

    expected = _draw(model.rng)

    restored = Model.from_snapshot(snapshot)

    assert _draw(restored.rng) == expected


@pytest.mark.parametrize(
    "missing_field",
    [
        "rng_stream_policy",
        "rng_stream_root",
        "rng_streams",
    ],
)
def test_snapshot_rejects_partial_named_rng_fields(
    missing_field: str,
) -> None:
    snapshot = Model(seed=42).snapshot()
    snapshot.pop(missing_field)

    with pytest.raises(
        ValueError,
        match="must be provided together",
    ):
        Model.from_snapshot(snapshot)


def test_snapshot_rejects_unknown_named_rng_policy() -> None:
    snapshot = Model(seed=42).snapshot()
    snapshot["rng_stream_policy"] = "named-rng-streams-v999"

    with pytest.raises(
        ValueError,
        match="Unsupported RNG stream policy",
    ):
        Model.from_snapshot(snapshot)


@pytest.mark.parametrize(
    "root",
    [
        42,
        "0" * 63,
        "z" * 64,
    ],
)
def test_snapshot_rejects_invalid_named_rng_root(
    root: Any,
) -> None:
    snapshot = Model(seed=42).snapshot()
    snapshot["rng_stream_root"] = root

    with pytest.raises(
        ValueError,
        match="rng_stream_root",
    ):
        Model.from_snapshot(snapshot)


def test_snapshot_rejects_non_mapping_stream_collection() -> None:
    snapshot = Model(seed=42).snapshot()
    snapshot["rng_streams"] = []

    with pytest.raises(
        ValueError,
        match="'rng_streams' must be a mapping",
    ):
        Model.from_snapshot(snapshot)


@pytest.mark.parametrize(
    "invalid_name",
    [
        1,
        "",
        " scheduler ",
    ],
)
def test_snapshot_rejects_invalid_stream_names(
    invalid_name: Any,
) -> None:
    model = Model(seed=42)
    model.rng_stream("valid")

    snapshot = model.snapshot()
    valid_state = deepcopy(snapshot["rng_streams"]["valid"])
    snapshot["rng_streams"] = {invalid_name: valid_state}

    with pytest.raises(
        ValueError,
        match="stream names",
    ):
        Model.from_snapshot(snapshot)


def test_snapshot_rejects_non_mapping_stream_state() -> None:
    snapshot = Model(seed=42).snapshot()
    snapshot["rng_streams"] = {"scheduler": "not-a-mapping"}

    with pytest.raises(
        ValueError,
        match="must be a mapping",
    ):
        Model.from_snapshot(snapshot)


def test_snapshot_rejects_invalid_bit_generator_state() -> None:
    snapshot = Model(seed=42).snapshot()
    snapshot["rng_streams"] = {
        "scheduler": {
            "bit_generator": "PCG64",
        }
    }

    with pytest.raises(
        ValueError,
        match="Invalid RNG state for named stream",
    ):
        Model.from_snapshot(snapshot)


def test_snapshot_serializes_streams_in_name_order() -> None:
    model = Model(seed=42)

    model.rng_stream("zeta")
    model.rng_stream("alpha")
    model.rng_stream("scheduler")

    snapshot = model.snapshot()

    assert list(snapshot["rng_streams"]) == [
        "alpha",
        "scheduler",
        "zeta",
    ]


def test_named_rng_streams_survive_json_roundtrip(
    tmp_path: Any,
) -> None:
    model = Model(seed=42)

    scheduler_rng = model.rng_stream("scheduler")
    event_rng = model.rng_stream("events")

    scheduler_rng.random(9)
    event_rng.random(4)

    path = write_snapshot(
        model.snapshot(),
        tmp_path / "named-rng-snapshot.json",
    )
    loaded = read_snapshot(path)

    expected_scheduler = _draw(scheduler_rng)
    expected_events = _draw(event_rng)

    restored = Model.from_snapshot(loaded)

    assert _draw(restored.rng_stream("scheduler")) == expected_scheduler
    assert _draw(restored.rng_stream("events")) == expected_events
