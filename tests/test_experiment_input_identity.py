from __future__ import annotations

from pathlib import Path

import pytest

from abmforge.core.model import Model
from abmforge.experiment.experiment import Experiment
from abmforge.experiment.scenario import Scenario
from abmforge.repro.execution_fingerprint import ExecutionFingerprintV3


class ExperimentInputTestModel(Model):
    pass


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def test_experiment_propagates_declared_inputs_to_generated_scenarios(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    experiment = Experiment(
        model=ExperimentInputTestModel,
        parameters={"alpha": [1, 2]},
        seeds=[10, 11],
        steps=2,
        name="input-sweep",
        input_artifacts=[input_path],
        input_root=root,
    )

    scenarios = experiment.scenarios()

    assert len(scenarios) == 4

    for scenario in scenarios:
        assert list(scenario.input_artifacts) == [input_path]
        assert scenario.input_root == root

        fingerprint = scenario.execution_fingerprint()

        assert isinstance(fingerprint, ExecutionFingerprintV3)
        assert fingerprint.input_artifact_count == 1


def test_experiment_input_identity_uses_bytes_at_fingerprint_time(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    experiment = Experiment(
        model=ExperimentInputTestModel,
        parameters={"alpha": [1]},
        seeds=[10],
        steps=1,
        input_artifacts=[input_path],
        input_root=root,
    )

    scenario = experiment.scenarios()[0]
    first = scenario.execution_fingerprint()

    input_path.write_bytes(b"value\n2\n")

    second = scenario.execution_fingerprint()

    assert first.input_artifacts_sha256 != second.input_artifacts_sha256
    assert first.digest != second.digest


def test_experiment_declared_inputs_require_root_at_fingerprint_time(
    tmp_path: Path,
) -> None:
    input_path = _write(
        tmp_path / "input.csv",
        "value\n1\n",
    )

    experiment = Experiment(
        model=ExperimentInputTestModel,
        steps=1,
        input_artifacts=[input_path],
    )

    scenario = experiment.scenarios()[0]

    with pytest.raises(
        ValueError,
        match="input_root is required",
    ):
        scenario.execution_fingerprint()


def test_experiment_rejects_scalar_input_artifact_argument() -> None:
    with pytest.raises(
        TypeError,
        match="sequence of paths",
    ):
        Experiment(
            model=ExperimentInputTestModel,
            input_artifacts="input.csv",
        )


def test_experiment_level_inputs_are_not_silently_applied_to_explicit_scenarios(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "input.csv",
        "value\n1\n",
    )

    explicit = Scenario(
        model=ExperimentInputTestModel,
        steps=1,
    )

    with pytest.raises(
        ValueError,
        match="explicit scenarios",
    ):
        Experiment(
            scenarios=[explicit],
            input_artifacts=[input_path],
            input_root=root,
        )


def test_experiment_recovery_is_input_aware_end_to_end(
    tmp_path: Path,
) -> None:
    from abmforge.experiment.run_index import RunIndex

    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    experiment = Experiment(
        model=ExperimentInputTestModel,
        parameters={"alpha": [1]},
        seeds=[42],
        steps=1,
        name="end-to-end-input-recovery",
        input_artifacts=[input_path],
        input_root=root,
    )

    first_result = experiment.run()

    assert first_result.run_count == 1

    first_run = first_result.results[0]
    stored = first_run.dataset.runs[-1]["execution_fingerprint"]

    assert stored["schema_version"] == "execution-fingerprint-v3"
    assert stored["input_artifact_count"] == 1

    run_index = RunIndex.from_dataset(first_run.dataset)

    unchanged_result = experiment.run(run_index=run_index)

    assert unchanged_result.run_count == 0

    input_path.write_bytes(b"value\n2\n")

    changed_result = experiment.run(run_index=run_index)

    assert changed_result.run_count == 1

    changed_stored = changed_result.results[0].dataset.runs[-1]["execution_fingerprint"]

    assert changed_stored["schema_version"] == "execution-fingerprint-v3"
    assert changed_stored["input_artifacts_sha256"] != stored["input_artifacts_sha256"]
    assert changed_stored["digest"] != stored["digest"]
