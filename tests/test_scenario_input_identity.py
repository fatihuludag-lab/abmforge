from __future__ import annotations

from pathlib import Path

import pytest

from abmforge.core.model import Model
from abmforge.experiment.scenario import Scenario
from abmforge.repro.execution_fingerprint import (
    EXECUTION_FINGERPRINT_SCHEMA_VERSION,
    ExecutionFingerprintV3,
)
from abmforge.repro.input_provenance import DeclaredInputIdentityV1


class ScenarioInputTestModel(Model):
    pass


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def test_scenario_execution_fingerprint_uses_v3_without_inputs() -> None:
    scenario = Scenario(
        model=ScenarioInputTestModel,
        parameters={"alpha": 1},
        seed=101,
        steps=2,
        name="no-inputs",
    )

    fingerprint = scenario.execution_fingerprint()

    expected_inputs = DeclaredInputIdentityV1.from_paths([])

    assert isinstance(fingerprint, ExecutionFingerprintV3)
    assert fingerprint.schema_version == "execution-fingerprint-v3"
    assert fingerprint.input_artifact_count == 0
    assert fingerprint.input_artifacts_sha256 == expected_inputs.artifacts_sha256
    assert EXECUTION_FINGERPRINT_SCHEMA_VERSION == "execution-fingerprint-v3"


def test_scenario_execution_fingerprint_tracks_input_content(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    scenario = Scenario(
        model=ScenarioInputTestModel,
        parameters={"alpha": 1},
        seed=102,
        steps=2,
        name="input-change",
        input_artifacts=[input_path],
        input_root=root,
    )

    first = scenario.execution_fingerprint()

    input_path.write_bytes(b"value\n2\n")

    second = scenario.execution_fingerprint()

    assert first.input_artifact_count == 1
    assert second.input_artifact_count == 1
    assert first.input_artifacts_sha256 != second.input_artifacts_sha256
    assert first.digest != second.digest


def test_scenario_declared_inputs_require_input_root(
    tmp_path: Path,
) -> None:
    input_path = _write(
        tmp_path / "input.csv",
        "value\n1\n",
    )

    scenario = Scenario(
        model=ScenarioInputTestModel,
        input_artifacts=[input_path],
        steps=1,
    )

    with pytest.raises(
        ValueError,
        match="input_root is required",
    ):
        scenario.execution_fingerprint()


def test_scenario_run_persists_v3_input_identity(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    scenario = Scenario(
        model=ScenarioInputTestModel,
        parameters={"alpha": 1},
        seed=103,
        steps=0,
        name="persist-inputs",
        input_artifacts=[input_path],
        input_root=root,
    )

    planned = scenario.execution_fingerprint()
    result = scenario.run()
    stored = result.dataset.runs[-1]["execution_fingerprint"]

    assert stored["schema_version"] == "execution-fingerprint-v3"
    assert stored["input_artifact_count"] == 1
    assert stored["input_artifacts_sha256"] == planned.input_artifacts_sha256
    assert stored["digest"] == planned.digest
    assert ExecutionFingerprintV3.from_dict(stored) == planned


def test_scenario_input_order_does_not_change_fingerprint(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    first_path = _write(root / "data" / "a.csv", "value\n1\n")
    second_path = _write(root / "data" / "b.csv", "value\n2\n")

    first = Scenario(
        model=ScenarioInputTestModel,
        seed=104,
        steps=1,
        input_artifacts=[first_path, second_path],
        input_root=root,
    )

    second = Scenario(
        model=ScenarioInputTestModel,
        seed=104,
        steps=1,
        input_artifacts=[second_path, first_path],
        input_root=root,
    )

    assert first.execution_fingerprint().digest == second.execution_fingerprint().digest
