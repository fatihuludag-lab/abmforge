from __future__ import annotations

from abmforge.core.model import Model
from abmforge.experiment.recovery import missing_scenarios
from abmforge.experiment.run_index import RunIndex, RunIndexEntry
from abmforge.experiment.scenario import Scenario


class RecoveryTestModel(Model):
    """Minimal model used by experiment recovery tests."""


def test_missing_scenarios_skips_completed_archive_run() -> None:
    completed = Scenario(
        model=RecoveryTestModel,
        parameters={"growth_rate": 0.1},
        seed=101,
        steps=10,
        name="baseline",
    )
    missing = Scenario(
        model=RecoveryTestModel,
        parameters={"growth_rate": 0.2},
        seed=102,
        steps=10,
        name="baseline",
    )

    run_index = RunIndex(
        entries=[
            RunIndexEntry(
                run_id="run-existing",
                scenario="baseline",
                model_name="RecoveryTestModel",
                seed=101,
                status="completed",
                parameters={"growth_rate": 0.1},
            )
        ]
    )

    result = missing_scenarios(
        [completed, missing],
        run_index,
    )

    assert result == [missing]


def test_missing_scenarios_ignores_parameter_order() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1, "beta": 2},
        seed=201,
        steps=5,
        name="ordered",
    )

    run_index = RunIndex(
        entries=[
            RunIndexEntry(
                run_id="run-existing",
                scenario="ordered",
                model_name="RecoveryTestModel",
                seed=201,
                status="completed",
                parameters={"beta": 2, "alpha": 1},
            )
        ]
    )

    result = missing_scenarios([scenario], run_index)

    assert result == []


def test_missing_scenarios_reruns_non_completed_archive_run() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"growth_rate": 0.3},
        seed=301,
        steps=10,
        name="retry",
    )

    run_index = RunIndex(
        entries=[
            RunIndexEntry(
                run_id="run-failed",
                scenario="retry",
                model_name="RecoveryTestModel",
                seed=301,
                status="failed",
                parameters={"growth_rate": 0.3},
            )
        ]
    )

    result = missing_scenarios([scenario], run_index)

    assert result == [scenario]


def test_missing_scenarios_preserves_duplicate_runs() -> None:
    scenario1 = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=500,
        steps=5,
        name="baseline",
    )

    scenario2 = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=500,
        steps=5,
        name="baseline",
    )

    scenario3 = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=500,
        steps=5,
        name="baseline",
    )

    run_index = RunIndex(
        entries=[
            RunIndexEntry(
                run_id="run-existing",
                scenario="baseline",
                model_name="RecoveryTestModel",
                seed=500,
                status="completed",
                parameters={"alpha": 1},
            )
        ]
    )

    result = missing_scenarios(
        [scenario1, scenario2, scenario3],
        run_index,
    )

    assert result == [scenario2, scenario3]


def test_missing_scenarios_returns_all_when_archive_is_empty() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1,
        steps=5,
        name="baseline",
    )

    result = missing_scenarios([scenario], RunIndex())

    assert result == [scenario]


def test_missing_scenarios_returns_empty_for_empty_plan() -> None:
    result = missing_scenarios([], RunIndex())

    assert result == []
