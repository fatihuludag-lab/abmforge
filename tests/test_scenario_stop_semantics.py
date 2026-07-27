from __future__ import annotations

from abmforge.core.model import Model
from abmforge.experiment.scenario import Scenario


class StopInsideStepModel(Model):
    def step(self) -> None:
        self.stop("internal_stop")


class StopInSetupModel(Model):
    def setup(self) -> None:
        self.stop("setup_stop")

    def step(self) -> None:
        raise AssertionError("Scenario should not step a model stopped in setup")


def test_scenario_respects_model_stop_called_inside_step() -> None:
    scenario = Scenario(model=StopInsideStepModel, steps=5)

    result = scenario.run()

    assert result.status == "stopped"
    assert result.steps == 1
    assert result.stop_reason == "internal_stop"
    assert result.model is not None
    assert result.model.steps == 1
    assert result.model.status == "stopped"
    assert result.model.running is False


def test_scenario_respects_model_stop_called_during_setup() -> None:
    scenario = Scenario(model=StopInSetupModel, steps=5)

    result = scenario.run()

    assert result.status == "stopped"
    assert result.steps == 0
    assert result.stop_reason == "setup_stop"
    assert result.model is not None
    assert result.model.steps == 0
    assert result.model.status == "stopped"
    assert result.model.running is False


class LifecycleObservationModel(Model):
    def step(self) -> None:
        pass


def test_scenario_remains_running_until_multi_step_execution_finishes() -> None:
    observations: list[tuple[str, bool, int]] = []

    def observe_lifecycle(model: Model) -> bool:
        observations.append((model.status, model.running, model.steps))
        return False

    scenario = Scenario(
        model=LifecycleObservationModel,
        steps=2,
        stop_when=observe_lifecycle,
    )

    result = scenario.run()

    assert observations
    assert all(status == "running" and running is True for status, running, _ in observations)
    assert result.status == "completed"
    assert result.model is not None
    assert result.model.status == "completed"
    assert result.model.running is False


def test_scenario_stop_condition_sets_stopped_inactive_state() -> None:
    def stop_after_one_step(model: Model) -> bool:
        return model.steps >= 1

    scenario = Scenario(
        model=LifecycleObservationModel,
        steps=5,
        stop_when=stop_after_one_step,
    )

    result = scenario.run()

    assert result.status == "stopped"
    assert result.steps == 1
    assert result.stop_reason == "stop_condition"
    assert result.model is not None
    assert result.model.status == "stopped"
    assert result.model.running is False
