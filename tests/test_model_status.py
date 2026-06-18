import pytest

from abmforge import Model, Scenario
from abmforge.core.status import (
    COMPLETED,
    CREATED,
    FAILED,
    RUNNING,
    STOPPED,
    VALID_MODEL_STATUSES,
    validate_model_status,
)


class StatusModel(Model):
    def step(self) -> None:
        pass


class FailingStatusModel(Model):
    def step(self) -> None:
        raise RuntimeError("boom")


def test_valid_model_statuses_are_explicit() -> None:
    assert {
        CREATED,
        RUNNING,
        COMPLETED,
        STOPPED,
        FAILED,
    } == VALID_MODEL_STATUSES


def test_validate_model_status_accepts_known_status() -> None:
    assert validate_model_status(CREATED) == CREATED
    assert validate_model_status(COMPLETED) == COMPLETED


def test_validate_model_status_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="Invalid model status"):
        validate_model_status("unknown")


def test_model_initial_status_is_created() -> None:
    model = StatusModel()

    assert model.status == CREATED


def test_model_run_for_sets_completed_status() -> None:
    model = StatusModel()

    model.run_for(1)

    assert model.status == COMPLETED
    assert model.steps == 1


def test_model_stop_sets_stopped_status() -> None:
    model = StatusModel()

    model.stop("manual")

    assert model.status == STOPPED
    assert model.stop_reason == "manual"


def test_scenario_zero_steps_marks_model_completed() -> None:
    scenario = Scenario(
        model=StatusModel,
        parameters={},
        seed=1,
        steps=0,
        name="zero_step_status",
    )

    result = scenario.run()

    assert result.status == COMPLETED
    assert result.model is not None
    assert result.model.status == COMPLETED
    assert result.dataset.runs[-1]["status"] == COMPLETED


def test_failed_scenario_uses_failed_status() -> None:
    scenario = Scenario(
        model=FailingStatusModel,
        parameters={},
        seed=1,
        steps=1,
        name="failing_status",
    )

    result = scenario.run(raise_on_error=False)

    assert result.status == FAILED
    assert result.model is not None
    assert result.model.status == FAILED
    assert result.dataset.runs[-1]["status"] == FAILED
