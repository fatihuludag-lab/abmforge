from __future__ import annotations

import pytest

from abmforge.core.agent import Agent
from abmforge.core.model import Model
from abmforge.scheduling import (
    RandomActivation,
    SequentialActivation,
    SimultaneousActivation,
    StagedActivation,
)


class LoggingAgent(Agent):
    def step(self) -> None:
        self.model.activation_log.append(self.unique_id)


class SpawningAgent(Agent):
    def step(self) -> None:
        self.model.activation_log.append(self.unique_id)

        if not getattr(self.model, "spawned", False):
            self.model.spawned = True
            self.spawn(LoggingAgent)


class SimultaneousAgent(Agent):
    def step(self) -> None:
        self.model.activation_log.append(f"step-{self.unique_id}")
        self.pending_value = self.unique_id

    def advance(self) -> None:
        self.model.activation_log.append(f"advance-{self.unique_id}")
        self.value = self.pending_value


class StagedAgent(Agent):
    def sense(self) -> None:
        self.model.activation_log.append(f"sense-{self.unique_id}")

    def decide(self) -> None:
        self.model.activation_log.append(f"decide-{self.unique_id}")

    def act(self) -> None:
        self.model.activation_log.append(f"act-{self.unique_id}")


def _model(seed: int | None = 42) -> Model:
    model = Model(seed=seed)
    model.activation_log = []
    return model


def test_sequential_activation_uses_insertion_order() -> None:
    model = _model()
    model.agents.create(LoggingAgent, n=3)

    SequentialActivation(model).step()

    assert model.activation_log == [1, 2, 3]


def test_sequential_activation_skips_dead_agents() -> None:
    model = _model()
    agents = model.agents.create(LoggingAgent, n=3)
    agents[1].is_alive = False

    SequentialActivation(model).step()

    assert model.activation_log == [1, 3]


def test_sequential_activation_does_not_activate_new_agents_in_same_pass() -> None:
    model = _model()
    model.spawned = False
    model.agents.create(SpawningAgent, n=1)

    SequentialActivation(model).step()

    assert model.activation_log == [1]
    assert len(model.agents) == 2


def test_random_activation_is_reproducible_with_same_seed() -> None:
    def order(seed: int) -> list[int]:
        model = _model(seed=seed)
        model.agents.create(LoggingAgent, n=20)
        RandomActivation(model).step()
        return list(model.activation_log)

    assert order(42) == order(42)


def test_random_activation_activates_each_alive_agent_once() -> None:
    model = _model(seed=7)
    agents = model.agents.create(LoggingAgent, n=10)
    agents[3].is_alive = False

    RandomActivation(model).step()

    assert sorted(model.activation_log) == [1, 2, 3, 5, 6, 7, 8, 9, 10]


def test_simultaneous_activation_calls_all_steps_before_advances() -> None:
    model = _model()
    agents = model.agents.create(SimultaneousAgent, n=2)

    SimultaneousActivation(model).step()

    assert model.activation_log == [
        "step-1",
        "step-2",
        "advance-1",
        "advance-2",
    ]
    assert agents[0].value == 1
    assert agents[1].value == 2


def test_simultaneous_activation_skips_dead_agents() -> None:
    model = _model()
    agents = model.agents.create(SimultaneousAgent, n=3)
    agents[1].is_alive = False

    SimultaneousActivation(model).step()

    assert model.activation_log == [
        "step-1",
        "step-3",
        "advance-1",
        "advance-3",
    ]


def test_staged_activation_uses_declared_stage_order() -> None:
    model = _model()
    model.agents.create(StagedAgent, n=2)

    StagedActivation(model, stages=["sense", "decide", "act"]).step()

    assert model.activation_log == [
        "sense-1",
        "sense-2",
        "decide-1",
        "decide-2",
        "act-1",
        "act-2",
    ]


def test_staged_activation_skips_dead_agents() -> None:
    model = _model()
    agents = model.agents.create(StagedAgent, n=3)
    agents[1].is_alive = False

    StagedActivation(model, stages=["sense", "act"]).step()

    assert model.activation_log == [
        "sense-1",
        "sense-3",
        "act-1",
        "act-3",
    ]


def test_staged_activation_shuffle_is_reproducible_with_same_seed() -> None:
    def order(seed: int) -> list[str]:
        model = _model(seed=seed)
        model.agents.create(StagedAgent, n=10)
        StagedActivation(model, stages=["act"], shuffle=True).step()
        return list(model.activation_log)

    assert order(123) == order(123)


class MissingStageAgent(Agent):
    def sense(self) -> None:
        self.model.activation_log.append(f"sense-{self.unique_id}")


def test_staged_activation_rejects_empty_stages() -> None:
    model = _model()

    with pytest.raises(ValueError, match="at least one stage"):
        StagedActivation(model, stages=[])


def test_staged_activation_rejects_string_as_stage_sequence() -> None:
    model = _model()

    with pytest.raises(ValueError, match="sequence of stage names"):
        StagedActivation(model, stages="act")  # type: ignore[arg-type]


def test_staged_activation_rejects_non_empty_string_stage_names() -> None:
    model = _model()

    with pytest.raises(ValueError, match=r"stages\[0\] must be a non-empty string"):
        StagedActivation(model, stages=[""])


def test_staged_activation_reports_missing_stage_method() -> None:
    model = _model()
    model.agents.create(MissingStageAgent, n=1)

    scheduler = StagedActivation(model, stages=["sense", "act"])

    with pytest.raises(AttributeError, match="stage method 'act'"):
        scheduler.step()


def test_staged_activation_calls_optional_model_stage_hooks() -> None:
    model = _model()

    def before_stage(stage: str) -> None:
        model.activation_log.append(f"before-{stage}")

    def after_stage(stage: str) -> None:
        model.activation_log.append(f"after-{stage}")

    model.before_stage = before_stage
    model.after_stage = after_stage
    model.agents.create(StagedAgent, n=1)

    StagedActivation(model, stages=["sense", "act"]).step()

    assert model.activation_log == [
        "before-sense",
        "sense-1",
        "after-sense",
        "before-act",
        "act-1",
        "after-act",
    ]


def test_staged_activation_rejects_non_callable_stage_hooks() -> None:
    model = _model()
    model.before_stage = "not-callable"
    model.agents.create(StagedAgent, n=1)

    scheduler = StagedActivation(model, stages=["sense"])

    with pytest.raises(TypeError, match="model.before_stage must be callable"):
        scheduler.step()
