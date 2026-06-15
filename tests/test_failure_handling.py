from __future__ import annotations

import csv
import json

import pytest

from abmforge import Experiment, Model, Scenario


class EmptyModel(Model):
    """A model that completes successfully."""


class FailingSetupModel(Model):
    """A model that fails during setup."""

    def setup(self) -> None:
        raise RuntimeError("intentional setup failure")


class FailingConstructorModel(Model):
    """A model that fails during construction."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        raise RuntimeError("intentional constructor failure")


def test_scenario_raises_by_default_and_records_failure_metadata() -> None:
    scenario = Scenario(model=FailingSetupModel, seed=1, steps=1)

    with pytest.raises(RuntimeError, match="intentional setup failure"):
        scenario.run()


def test_scenario_can_return_failed_result_without_raising() -> None:
    scenario = Scenario(model=FailingSetupModel, seed=1, steps=1)

    result = scenario.run(raise_on_error=False)

    assert result.status == "failed"
    assert result.error is not None
    assert result.exception_type == "RuntimeError"
    assert result.dataset.runs[-1]["status"] == "failed"
    assert result.dataset.runs[-1]["exception_type"] == "RuntimeError"
    assert result.dataset.errors
    assert result.dataset.errors[-1]["exception_type"] == "RuntimeError"
    assert result.dataset.errors[-1]["component"] == "Scenario.run"
    assert "intentional setup failure" in result.dataset.errors[-1]["message"]
    assert result.dataset.errors[-1]["traceback"] is not None


def test_experiment_continue_on_error_keeps_failed_runs() -> None:
    experiment = Experiment(
        scenarios=[
            Scenario(model=EmptyModel, seed=1, steps=0, name="ok"),
            Scenario(model=FailingSetupModel, seed=2, steps=1, name="bad"),
        ],
        continue_on_error=True,
    )

    result = experiment.run()

    assert len(result) == 2
    assert result.run_count == 2
    assert result.failed_count == 1
    assert len(result.successful()) == 1
    assert len(result.failed()) == 1
    assert result.statuses() == {"completed": 1, "failed": 1}

    failed = result.failed()[0]
    assert failed.status == "failed"
    assert failed.error is not None
    assert failed.dataset.errors
    assert failed.dataset.runs[-1]["status"] == "failed"


def test_experiment_raises_when_continue_on_error_is_false() -> None:
    experiment = Experiment(
        scenarios=[
            Scenario(model=EmptyModel, seed=1, steps=0, name="ok"),
            Scenario(model=FailingSetupModel, seed=2, steps=1, name="bad"),
        ],
        continue_on_error=False,
    )

    with pytest.raises(RuntimeError, match="intentional setup failure"):
        experiment.run()


def test_experiment_csv_export_includes_errors(tmp_path) -> None:  # type: ignore[no-untyped-def]
    experiment = Experiment(
        scenarios=[
            Scenario(model=EmptyModel, seed=1, steps=0, name="ok"),
            Scenario(model=FailingSetupModel, seed=2, steps=1, name="bad"),
        ],
        continue_on_error=True,
    )

    result = experiment.run()
    output_dir = result.write_csv(tmp_path)

    errors_csv = output_dir / "errors.csv"

    assert errors_csv.exists()

    with errors_csv.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["exception_type"] == "RuntimeError"
    assert "intentional setup failure" in rows[0]["message"]


def test_dataset_json_export_includes_errors(tmp_path) -> None:  # type: ignore[no-untyped-def]
    result = Scenario(
        model=FailingSetupModel,
        seed=1,
        steps=1,
    ).run(raise_on_error=False)

    output_dir = result.dataset.write_json(tmp_path)
    errors_jsonl = output_dir / "errors.jsonl"

    assert errors_jsonl.exists()

    lines = errors_jsonl.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    error_record = json.loads(lines[0])
    assert error_record["exception_type"] == "RuntimeError"
    assert "intentional setup failure" in error_record["message"]


def test_constructor_failure_can_be_returned_as_failed_result() -> None:
    scenario = Scenario(model=FailingConstructorModel, seed=1, steps=1)

    result = scenario.run(raise_on_error=False)

    assert result.status == "failed"
    assert result.model is None
    assert result.exception_type == "RuntimeError"
    assert result.dataset.runs[-1]["status"] == "failed"
    assert result.dataset.errors[-1]["component"] == "Scenario.construct"
    assert "intentional constructor failure" in result.dataset.errors[-1]["message"]
