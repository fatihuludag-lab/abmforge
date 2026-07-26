from __future__ import annotations

from abmforge.core.model import Model
from abmforge.experiment.recovery import missing_scenarios
from abmforge.experiment.run_index import (
    RUN_IDENTITY_SCHEMA_VERSION,
    RunIndex,
    RunIndexEntry,
)
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
                model_module=RecoveryTestModel.__module__,
                model_qualname=RecoveryTestModel.__qualname__,
                run_identity_version=RUN_IDENTITY_SCHEMA_VERSION,
                seed=101,
                status="completed",
                steps=10,
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
                model_module=RecoveryTestModel.__module__,
                model_qualname=RecoveryTestModel.__qualname__,
                run_identity_version=RUN_IDENTITY_SCHEMA_VERSION,
                seed=201,
                status="completed",
                steps=5,
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
                model_module=RecoveryTestModel.__module__,
                model_qualname=RecoveryTestModel.__qualname__,
                run_identity_version=RUN_IDENTITY_SCHEMA_VERSION,
                seed=500,
                status="completed",
                steps=5,
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


def test_missing_scenarios_does_not_match_different_step_counts() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"growth_rate": 0.1},
        seed=101,
        steps=100,
        name="baseline",
    )

    run_index = RunIndex(
        entries=[
            RunIndexEntry(
                run_id="run-existing",
                scenario="baseline",
                model_name="RecoveryTestModel",
                model_module=RecoveryTestModel.__module__,
                model_qualname=RecoveryTestModel.__qualname__,
                run_identity_version=RUN_IDENTITY_SCHEMA_VERSION,
                seed=101,
                status="completed",
                steps=10,
                parameters={"growth_rate": 0.1},
            )
        ]
    )

    result = missing_scenarios([scenario], run_index)

    assert result == [scenario]


def test_missing_scenarios_does_not_match_same_model_name_from_different_module() -> None:
    archived_model = type(
        "SharedModel",
        (Model,),
        {"__module__": "archived_package.models"},
    )
    planned_model = type(
        "SharedModel",
        (Model,),
        {"__module__": "planned_package.models"},
    )

    scenario = Scenario(
        model=planned_model,
        parameters={"alpha": 1},
        seed=701,
        steps=5,
        name="module-check",
    )

    run_index = RunIndex(
        entries=[
            RunIndexEntry(
                run_id="run-existing",
                scenario="module-check",
                model_name=archived_model.__name__,
                model_module=archived_model.__module__,
                model_qualname=archived_model.__qualname__,
                run_identity_version=RUN_IDENTITY_SCHEMA_VERSION,
                seed=701,
                status="completed",
                steps=5,
                parameters={"alpha": 1},
            )
        ]
    )

    result = missing_scenarios([scenario], run_index)

    assert result == [scenario]


def test_missing_scenarios_matches_run_index_created_from_actual_scenario_run() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=801,
        steps=1,
        name="actual-run",
    )

    run_result = scenario.run()
    run_index = RunIndex.from_dataset(run_result.dataset)

    result = missing_scenarios([scenario], run_index)

    assert result == []
    assert run_index.entries[0].model_module == RecoveryTestModel.__module__
    assert run_index.entries[0].model_qualname == RecoveryTestModel.__qualname__


def test_missing_scenarios_does_not_trust_legacy_incomplete_run_identity() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=901,
        steps=5,
        name="legacy-check",
    )

    legacy_run_index = RunIndex(
        entries=[
            RunIndexEntry(
                run_id="legacy-run",
                scenario="legacy-check",
                model_name="RecoveryTestModel",
                seed=901,
                status="completed",
                parameters={"alpha": 1},
            )
        ]
    )

    result = missing_scenarios([scenario], legacy_run_index)

    assert result == [scenario]


def test_missing_scenarios_does_not_recover_programmatic_stop_condition() -> None:
    def never_stop(model: Model) -> bool:
        return False

    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1001,
        steps=10,
        stop_when=never_stop,
        name="conditional-stop",
    )

    run_result = scenario.run()
    run_index = RunIndex.from_dataset(run_result.dataset)

    result = missing_scenarios([scenario], run_index)

    assert result == [scenario]


def test_actual_run_persists_versioned_recovery_identity() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1101,
        steps=2,
        name="versioned-identity",
    )

    run_result = scenario.run()
    run_index = RunIndex.from_dataset(run_result.dataset)
    entry = run_index.entries[0]

    assert entry.run_identity_version == RUN_IDENTITY_SCHEMA_VERSION


def test_missing_scenarios_does_not_match_different_identity_version() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1201,
        steps=5,
        name="identity-version",
    )

    run_index = RunIndex(
        entries=[
            RunIndexEntry(
                run_id="future-run",
                scenario="identity-version",
                model_name=RecoveryTestModel.__name__,
                model_module=RecoveryTestModel.__module__,
                model_qualname=RecoveryTestModel.__qualname__,
                run_identity_version="run-identity-v2",
                seed=1201,
                status="completed",
                steps=5,
                parameters={"alpha": 1},
            )
        ]
    )

    result = missing_scenarios([scenario], run_index)

    assert result == [scenario]
