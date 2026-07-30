from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from abmforge import Agent, Model
from abmforge.scheduling import (
    RandomActivation,
    SequentialActivation,
    SimultaneousActivation,
    StagedActivation,
)


class _FixedPermutationRng:
    """Return insertion order for deterministic activation tests."""

    def permutation(self, size: int) -> list[int]:
        return list(range(size))


class _TrackingAgent(Agent):
    def __init__(
        self,
        model: Model,
        unique_id: int,
        *,
        label: str,
        log: list[str],
        callbacks: dict[str, Callable[[], None]] | None = None,
    ) -> None:
        super().__init__(model=model, unique_id=unique_id)
        self.label = label
        self.log = log
        self.callbacks = callbacks or {}

    def _call(self, method_name: str) -> None:
        self.log.append(f"{self.label}.{method_name}")

        callback = self.callbacks.get(method_name)
        if callback is not None:
            callback()

    def step(self) -> None:
        self._call("step")

    def advance(self) -> None:
        self._call("advance")

    def sense(self) -> None:
        self._call("sense")

    def act(self) -> None:
        self._call("act")


def _make_removal_model() -> tuple[Model, list[str]]:
    model = Model(seed=42)
    log: list[str] = []

    remover = _TrackingAgent(
        model,
        1,
        label="remover",
        log=log,
        callbacks={
            "step": lambda: model.agents.remove(2),
            "sense": lambda: model.agents.remove(2),
        },
    )
    target = _TrackingAgent(
        model,
        2,
        label="target",
        log=log,
    )
    survivor = _TrackingAgent(
        model,
        3,
        label="survivor",
        log=log,
    )

    model.agents.add(remover)
    model.agents.add(target)
    model.agents.add(survivor)

    return model, log


def test_collection_do_skips_agent_removed_before_its_turn() -> None:
    model, log = _make_removal_model()

    model.agents.do("step")

    assert log == [
        "remover.step",
        "survivor.step",
    ]
    assert [agent.unique_id for agent in model.agents] == [1, 3]


def test_collection_shuffle_do_skips_agent_removed_before_its_turn() -> None:
    model, log = _make_removal_model()
    model._rng_streams["scheduler"] = cast(Any, _FixedPermutationRng())

    model.agents.shuffle_do("step")

    assert log == [
        "remover.step",
        "survivor.step",
    ]
    assert [agent.unique_id for agent in model.agents] == [1, 3]


def test_sequential_activation_skips_removed_agent() -> None:
    model, log = _make_removal_model()

    SequentialActivation(model).step()

    assert log == [
        "remover.step",
        "survivor.step",
    ]


def test_random_activation_skips_removed_agent() -> None:
    model, log = _make_removal_model()
    model._rng_streams["scheduler"] = cast(Any, _FixedPermutationRng())

    RandomActivation(model).step()

    assert log == [
        "remover.step",
        "survivor.step",
    ]


def test_simultaneous_activation_skips_removed_agent_in_both_phases() -> None:
    model, log = _make_removal_model()

    SimultaneousActivation(model).step()

    assert log == [
        "remover.step",
        "survivor.step",
        "remover.advance",
        "survivor.advance",
    ]


def test_staged_activation_skips_removed_agent_in_all_remaining_stages() -> None:
    model, log = _make_removal_model()

    StagedActivation(
        model,
        stages=["sense", "act"],
    ).step()

    assert log == [
        "remover.sense",
        "survivor.sense",
        "remover.act",
        "survivor.act",
    ]


def test_replacing_removed_agent_with_same_id_activates_neither_object() -> None:
    model = Model(seed=42)
    log: list[str] = []

    def replace_target() -> None:
        old_target = model.agents.get(2)
        model.agents.remove(old_target)

        replacement = _TrackingAgent(
            model,
            2,
            label="replacement",
            log=log,
        )
        model.agents.add(replacement)

    remover = _TrackingAgent(
        model,
        1,
        label="remover",
        log=log,
        callbacks={"step": replace_target},
    )
    original = _TrackingAgent(
        model,
        2,
        label="original",
        log=log,
    )
    survivor = _TrackingAgent(
        model,
        3,
        label="survivor",
        log=log,
    )

    model.agents.add(remover)
    model.agents.add(original)
    model.agents.add(survivor)

    model.agents.do("step")

    assert log == [
        "remover.step",
        "survivor.step",
    ]
    assert model.agents.get(2) is not original


def test_collection_do_skips_agent_marked_not_alive() -> None:
    model = Model(seed=42)
    log: list[str] = []

    alive = _TrackingAgent(
        model,
        1,
        label="alive",
        log=log,
    )
    dead = _TrackingAgent(
        model,
        2,
        label="dead",
        log=log,
    )
    dead.is_alive = False

    model.agents.add(alive)
    model.agents.add(dead)

    model.agents.do("step")

    assert log == ["alive.step"]


def test_agent_added_during_collection_pass_is_deferred() -> None:
    model = Model(seed=42)
    log: list[str] = []

    def add_agent_once() -> None:
        if 3 not in model.agents:
            model.agents.add(
                _TrackingAgent(
                    model,
                    3,
                    label="new",
                    log=log,
                )
            )

    spawner = _TrackingAgent(
        model,
        1,
        label="spawner",
        log=log,
        callbacks={"step": add_agent_once},
    )
    existing = _TrackingAgent(
        model,
        2,
        label="existing",
        log=log,
    )

    model.agents.add(spawner)
    model.agents.add(existing)

    model.agents.do("step")

    assert log == [
        "spawner.step",
        "existing.step",
    ]
    assert [agent.unique_id for agent in model.agents] == [1, 2, 3]

    log.clear()
    model.agents.do("step")

    assert log == [
        "spawner.step",
        "existing.step",
        "new.step",
    ]
