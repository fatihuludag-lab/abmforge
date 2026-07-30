from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

import pytest

from abmforge import Agent, Model
from abmforge.scheduling import SimultaneousActivation

_CONTRACT_ERROR = (
    "SimultaneousActivation requires every eligible agent to define "
    "callable step() and advance() methods"
)


class _TwoPhaseAgent(Agent):
    def __init__(
        self,
        model: Model,
        unique_id: int,
        *,
        label: str,
        log: list[str],
        on_step: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            model=model,
            unique_id=unique_id,
        )
        self.label = label
        self.log = log
        self.on_step = on_step

    def step(self) -> None:
        self.log.append(f"{self.label}.step")

        if self.on_step is not None:
            self.on_step()

    def advance(self) -> None:
        self.log.append(f"{self.label}.advance")


class _AgentWithoutAdvance(Agent):
    def __init__(
        self,
        model: Model,
        unique_id: int,
        *,
        log: list[str],
    ) -> None:
        super().__init__(
            model=model,
            unique_id=unique_id,
        )
        self.log = log

    def step(self) -> None:
        self.log.append("missing_advance.step")


class _AgentWithNonCallableAdvance(Agent):
    advance: Any = None

    def __init__(
        self,
        model: Model,
        unique_id: int,
        *,
        log: list[str],
    ) -> None:
        super().__init__(
            model=model,
            unique_id=unique_id,
        )
        self.log = log

    def step(self) -> None:
        self.log.append("non_callable_advance.step")


class _AgentWithNonCallableStep(Agent):
    step: Any = None

    def __init__(
        self,
        model: Model,
        unique_id: int,
        *,
        log: list[str],
    ) -> None:
        super().__init__(
            model=model,
            unique_id=unique_id,
        )
        self.log = log

    def advance(self) -> None:
        self.log.append("non_callable_step.advance")


def test_missing_advance_is_rejected_before_any_callback() -> None:
    model = Model(seed=42)
    log: list[str] = []

    model.agents.add(
        _TwoPhaseAgent(
            model,
            1,
            label="valid",
            log=log,
        )
    )
    model.agents.add(
        _AgentWithoutAdvance(
            model,
            2,
            log=log,
        )
    )

    with pytest.raises(
        TypeError,
        match=re.escape(_CONTRACT_ERROR),
    ) as exc_info:
        SimultaneousActivation(model).step()

    assert log == []
    assert "2" in str(exc_info.value)
    assert "advance" in str(exc_info.value)


def test_non_callable_advance_is_rejected_before_any_callback() -> None:
    model = Model(seed=42)
    log: list[str] = []

    model.agents.add(
        _TwoPhaseAgent(
            model,
            1,
            label="valid",
            log=log,
        )
    )
    model.agents.add(
        _AgentWithNonCallableAdvance(
            model,
            2,
            log=log,
        )
    )

    with pytest.raises(
        TypeError,
        match=re.escape(_CONTRACT_ERROR),
    ) as exc_info:
        SimultaneousActivation(model).step()

    assert log == []
    assert "2" in str(exc_info.value)
    assert "advance" in str(exc_info.value)


def test_non_callable_step_is_rejected_before_any_callback() -> None:
    model = Model(seed=42)
    log: list[str] = []

    model.agents.add(
        _TwoPhaseAgent(
            model,
            1,
            label="valid",
            log=log,
        )
    )
    model.agents.add(
        _AgentWithNonCallableStep(
            model,
            2,
            log=log,
        )
    )

    with pytest.raises(
        TypeError,
        match=re.escape(_CONTRACT_ERROR),
    ) as exc_info:
        SimultaneousActivation(model).step()

    assert log == []
    assert "2" in str(exc_info.value)
    assert "step" in str(exc_info.value)


def test_all_invalid_agents_are_reported_before_activation() -> None:
    model = Model(seed=42)
    log: list[str] = []

    model.agents.add(
        _TwoPhaseAgent(
            model,
            1,
            label="valid",
            log=log,
        )
    )
    model.agents.add(
        _AgentWithoutAdvance(
            model,
            2,
            log=log,
        )
    )
    model.agents.add(
        _AgentWithNonCallableStep(
            model,
            3,
            log=log,
        )
    )

    with pytest.raises(
        TypeError,
        match=re.escape(_CONTRACT_ERROR),
    ) as exc_info:
        SimultaneousActivation(model).step()

    message = str(exc_info.value)

    assert log == []
    assert "2" in message
    assert "advance" in message
    assert "3" in message
    assert "step" in message


def test_two_phase_callbacks_run_in_strict_phase_order() -> None:
    model = Model(seed=42)
    log: list[str] = []

    model.agents.add(
        _TwoPhaseAgent(
            model,
            1,
            label="first",
            log=log,
        )
    )
    model.agents.add(
        _TwoPhaseAgent(
            model,
            2,
            label="second",
            log=log,
        )
    )

    SimultaneousActivation(model).step()

    assert log == [
        "first.step",
        "second.step",
        "first.advance",
        "second.advance",
    ]


def test_agent_removed_before_turn_is_skipped_in_both_phases() -> None:
    model = Model(seed=42)
    log: list[str] = []

    second = _TwoPhaseAgent(
        model,
        2,
        label="second",
        log=log,
    )
    first = _TwoPhaseAgent(
        model,
        1,
        label="first",
        log=log,
        on_step=second.remove,
    )

    model.agents.add(first)
    model.agents.add(second)

    SimultaneousActivation(model).step()

    assert log == [
        "first.step",
        "first.advance",
    ]


def test_self_removed_agent_does_not_enter_advance_phase() -> None:
    model = Model(seed=42)
    log: list[str] = []

    first = _TwoPhaseAgent(
        model,
        1,
        label="first",
        log=log,
    )
    first.on_step = first.remove

    second = _TwoPhaseAgent(
        model,
        2,
        label="second",
        log=log,
    )

    model.agents.add(first)
    model.agents.add(second)

    SimultaneousActivation(model).step()

    assert log == [
        "first.step",
        "second.step",
        "second.advance",
    ]


def test_same_id_replacement_waits_until_next_activation() -> None:
    model = Model(seed=42)
    log: list[str] = []

    old = _TwoPhaseAgent(
        model,
        2,
        label="old",
        log=log,
    )
    replacement = _TwoPhaseAgent(
        model,
        2,
        label="replacement",
        log=log,
    )

    first: _TwoPhaseAgent

    def replace_old() -> None:
        old.remove()
        model.agents.add(replacement)
        first.on_step = None

    first = _TwoPhaseAgent(
        model,
        1,
        label="first",
        log=log,
        on_step=replace_old,
    )

    model.agents.add(first)
    model.agents.add(old)

    scheduler = SimultaneousActivation(model)
    scheduler.step()

    assert log == [
        "first.step",
        "first.advance",
    ]

    scheduler.step()

    assert log == [
        "first.step",
        "first.advance",
        "first.step",
        "replacement.step",
        "first.advance",
        "replacement.advance",
    ]


def test_ineligible_agent_does_not_need_two_phase_capability() -> None:
    model = Model(seed=42)
    log: list[str] = []

    valid = _TwoPhaseAgent(
        model,
        1,
        label="valid",
        log=log,
    )
    inactive = _AgentWithoutAdvance(
        model,
        2,
        log=log,
    )

    model.agents.add(valid)
    model.agents.add(inactive)
    inactive.is_alive = False

    SimultaneousActivation(model).step()

    assert log == [
        "valid.step",
        "valid.advance",
    ]
