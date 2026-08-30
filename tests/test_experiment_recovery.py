from __future__ import annotations

from abmforge.core.model import Model
from abmforge.experiment.recovery import missing_scenarios
from abmforge.experiment.run_index import (
    RUN_IDENTITY_SCHEMA_VERSION,
    RunIndex,
    RunIndexEntry,
)
from abmforge.experiment.scenario import Scenario
from abmforge.experiment.scenario_schema import StopConditionV1
from abmforge.repro.execution_fingerprint import (
    ExecutionFingerprintV1,
    ExecutionFingerprintV2,
    ExecutionFingerprintV3,
)


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

    run_index = RunIndex.from_dataset(completed.run().dataset)

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

    run_index = RunIndex.from_dataset(scenario.run().dataset)
    run_index.entries[0].parameters = {"beta": 2, "alpha": 1}

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

    run_index = RunIndex.from_dataset(scenario1.run().dataset)

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

    archived = Scenario(
        model=RecoveryTestModel,
        parameters={"growth_rate": 0.1},
        seed=101,
        steps=10,
        name="baseline",
    )
    run_index = RunIndex.from_dataset(archived.run().dataset)

    result = missing_scenarios([scenario], run_index)

    assert result == [scenario]


def test_missing_scenarios_does_not_match_same_model_name_from_different_module(
    tmp_path,
) -> None:
    import importlib
    import sys
    from textwrap import dedent

    archived_module_name = f"archived_model_{tmp_path.name.replace('-', '_')}"
    planned_module_name = f"planned_model_{tmp_path.name.replace('-', '_')}"

    model_source = dedent(
        """
        from abmforge.core.model import Model


        class SharedModel(Model):
            pass
        """
    )
    (tmp_path / f"{archived_module_name}.py").write_text(
        model_source,
        encoding="utf-8",
    )
    (tmp_path / f"{planned_module_name}.py").write_text(
        model_source,
        encoding="utf-8",
    )
    importlib.invalidate_caches()

    sys.path.insert(0, str(tmp_path))
    try:
        archived_module = importlib.import_module(archived_module_name)
        planned_module = importlib.import_module(planned_module_name)

        archived = Scenario(
            model=archived_module.SharedModel,
            parameters={"alpha": 1},
            seed=701,
            steps=5,
            name="module-check",
        )
        planned = Scenario(
            model=planned_module.SharedModel,
            parameters={"alpha": 1},
            seed=701,
            steps=5,
            name="module-check",
        )
        run_index = RunIndex.from_dataset(archived.run().dataset)

        result = missing_scenarios([planned], run_index)
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop(archived_module_name, None)
        sys.modules.pop(planned_module_name, None)

    assert result == [planned]


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
    assert entry.execution_fingerprint == scenario.execution_fingerprint().to_dict()


def test_missing_scenarios_does_not_match_different_identity_version() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1201,
        steps=5,
        name="identity-version",
    )

    run_index = RunIndex.from_dataset(scenario.run().dataset)
    run_index.entries[0].run_identity_version = "run-identity-v999"

    result = missing_scenarios([scenario], run_index)

    assert result == [scenario]


def test_missing_scenarios_reruns_when_model_source_changes(tmp_path) -> None:
    import importlib
    import shutil
    import sys
    from textwrap import dedent

    module_name = f"recovery_source_change_{tmp_path.name.replace('-', '_')}"
    module_path = tmp_path / f"{module_name}.py"

    def write_model(*, increment: int) -> None:
        module_path.write_text(
            dedent(
                f"""
                from abmforge.core.model import Model


                class SourceChangedModel(Model):
                    def setup(self) -> None:
                        self.value = 0

                    def step(self) -> None:
                        self.value += {increment}
                """
            ),
            encoding="utf-8",
        )
        importlib.invalidate_caches()

    sys.path.insert(0, str(tmp_path))
    try:
        write_model(increment=1)
        archived_module = importlib.import_module(module_name)
        archived = Scenario(
            model=archived_module.SourceChangedModel,
            parameters={"alpha": 1},
            seed=1301,
            steps=2,
            name="source-change",
        )
        run_index = RunIndex.from_dataset(archived.run().dataset)

        sys.modules.pop(module_name, None)
        shutil.rmtree(tmp_path / "__pycache__", ignore_errors=True)

        write_model(increment=2)
        planned_module = importlib.import_module(module_name)
        planned = Scenario(
            model=planned_module.SourceChangedModel,
            parameters={"alpha": 1},
            seed=1301,
            steps=2,
            name="source-change",
        )

        result = missing_scenarios([planned], run_index)
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop(module_name, None)

    assert result == [planned]


def test_missing_scenarios_reruns_when_fingerprint_payload_is_tampered() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1401,
        steps=5,
        name="tampered-fingerprint",
    )
    run_index = RunIndex.from_dataset(scenario.run().dataset)
    entry = run_index.entries[0]

    assert entry.execution_fingerprint is not None
    tampered = dict(entry.execution_fingerprint)
    tampered["steps"] = 500
    entry.execution_fingerprint = tampered

    assert missing_scenarios([scenario], run_index) == [scenario]


def test_missing_scenarios_reruns_when_run_metadata_disagrees_with_fingerprint() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1501,
        steps=5,
        name="metadata-mismatch",
    )
    run_index = RunIndex.from_dataset(scenario.run().dataset)
    run_index.entries[0].model_module = "tampered.module"

    assert missing_scenarios([scenario], run_index) == [scenario]


def test_missing_scenarios_does_not_trust_v1_identity_with_fingerprint() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1601,
        steps=5,
        name="legacy-v1",
    )
    run_index = RunIndex.from_dataset(scenario.run().dataset)
    run_index.entries[0].run_identity_version = "run-identity-v1"

    assert missing_scenarios([scenario], run_index) == [scenario]


def test_missing_scenarios_reruns_when_fingerprint_digest_is_missing() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1701,
        steps=5,
        name="missing-digest",
    )
    run_index = RunIndex.from_dataset(scenario.run().dataset)
    entry = run_index.entries[0]

    assert entry.execution_fingerprint is not None
    without_digest = dict(entry.execution_fingerprint)
    without_digest.pop("digest")
    entry.execution_fingerprint = without_digest

    assert missing_scenarios([scenario], run_index) == [scenario]


def test_missing_scenarios_does_not_reuse_v1_fingerprint_under_v3_planner() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1801,
        steps=5,
        name="legacy-fingerprint-v1",
    )

    run_index = RunIndex.from_dataset(scenario.run().dataset)
    entry = run_index.entries[0]

    entry.execution_fingerprint = ExecutionFingerprintV1.create(
        model=scenario.model,
        scenario=scenario.name or scenario.model.__name__,
        seed=scenario.seed,
        steps=scenario.steps,
        parameters=scenario.parameters,
    ).to_dict()

    assert entry.execution_fingerprint["schema_version"] == "execution-fingerprint-v1"

    assert missing_scenarios([scenario], run_index) == [scenario]


def test_missing_scenarios_reruns_when_framework_tree_changes() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1901,
        steps=5,
        name="framework-change",
    )

    run_index = RunIndex.from_dataset(scenario.run().dataset)
    entry = run_index.entries[0]

    current = scenario.execution_fingerprint()
    assert current.framework_package_tree_sha256 is not None

    different_hash = "a" * 64 if current.framework_package_tree_sha256 != "a" * 64 else "b" * 64

    archived = ExecutionFingerprintV3.create(
        model=scenario.model,
        scenario=scenario.name or scenario.model.__name__,
        seed=scenario.seed,
        steps=scenario.steps,
        parameters=scenario.parameters,
        framework_version=current.framework_version,
        framework_package_tree_sha256=different_hash,
        declared_inputs=scenario.declared_input_identity(),
    )

    assert archived.trusted is True
    assert archived.digest != current.digest

    entry.execution_fingerprint = archived.to_dict()

    assert missing_scenarios([scenario], run_index) == [scenario]


def test_missing_scenarios_reuses_same_declared_inputs(tmp_path) -> None:
    root = tmp_path / "study"
    input_path = root / "data" / "observations.csv"
    input_path.parent.mkdir(parents=True)
    input_path.write_bytes(b"value\n1\n")

    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=2001,
        steps=2,
        name="input-reuse",
        input_artifacts=[input_path],
        input_root=root,
    )

    run_index = RunIndex.from_dataset(scenario.run().dataset)

    assert missing_scenarios([scenario], run_index) == []


def test_missing_scenarios_reruns_when_declared_input_content_changes(
    tmp_path,
) -> None:
    root = tmp_path / "study"
    input_path = root / "data" / "observations.csv"
    input_path.parent.mkdir(parents=True)
    input_path.write_bytes(b"value\n1\n")

    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=2002,
        steps=2,
        name="input-change",
        input_artifacts=[input_path],
        input_root=root,
    )

    run_index = RunIndex.from_dataset(scenario.run().dataset)

    input_path.write_bytes(b"value\n2\n")

    assert missing_scenarios([scenario], run_index) == [scenario]


def test_missing_scenarios_does_not_reuse_v2_under_v3_planner() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=2003,
        steps=2,
        name="legacy-v2-fingerprint",
    )

    run_index = RunIndex.from_dataset(scenario.run().dataset)
    entry = run_index.entries[0]

    current = scenario.execution_fingerprint()

    entry.execution_fingerprint = ExecutionFingerprintV2.create(
        model=scenario.model,
        scenario=scenario.name or scenario.model.__name__,
        seed=scenario.seed,
        steps=scenario.steps,
        parameters=scenario.parameters,
        framework_version=current.framework_version,
        framework_package_tree_sha256=(current.framework_package_tree_sha256),
    ).to_dict()

    assert entry.execution_fingerprint["schema_version"] == "execution-fingerprint-v2"
    assert missing_scenarios([scenario], run_index) == [scenario]


def test_missing_scenarios_does_not_recover_declarative_stop_condition() -> None:
    scenario = Scenario(
        model=RecoveryTestModel,
        parameters={"alpha": 1},
        seed=1401,
        steps=5,
        name="declarative-stop",
        stop_condition=StopConditionV1(
            field="steps",
            operator="ge",
            value=1,
        ),
    )

    run_result = scenario.run()
    run_index = RunIndex.from_dataset(run_result.dataset)

    result = missing_scenarios([scenario], run_index)

    assert result == [scenario]
