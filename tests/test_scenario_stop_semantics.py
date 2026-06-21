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


def test_scenario_respects_model_stop_called_during_setup() -> None:
    scenario = Scenario(model=StopInSetupModel, steps=5)

    result = scenario.run()

    assert result.status == "stopped"
    assert result.steps == 0
    assert result.stop_reason == "setup_stop"
    assert result.model is not None
    assert result.model.steps == 0
    assert result.model.status == "stopped"
