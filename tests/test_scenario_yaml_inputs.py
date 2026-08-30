from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from abmforge.experiment.scenario import Scenario
from abmforge.experiment.scenario_schema import (
    ScenarioSchemaV1,
    ScenarioValidationError,
)


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def test_scenario_schema_accepts_declared_inputs() -> None:
    schema = ScenarioSchemaV1.from_mapping(
        {
            "schema_version": "abmforge.scenario.v1",
            "model": "example.Model",
            "run": {
                "steps": 10,
            },
            "inputs": {
                "root": "..",
                "artifacts": [
                    "data/observations.csv",
                    "config/policy.json",
                ],
            },
        }
    )

    assert schema.input_root == ".."
    assert schema.input_artifacts == (
        "data/observations.csv",
        "config/policy.json",
    )


def test_scenario_schema_defaults_input_root_to_scenario_directory() -> None:
    schema = ScenarioSchemaV1.from_mapping(
        {
            "schema_version": "abmforge.scenario.v1",
            "model": "example.Model",
            "run": {
                "steps": 10,
            },
            "inputs": {
                "artifacts": [
                    "data/observations.csv",
                ],
            },
        }
    )

    assert schema.input_root == "."
    assert schema.input_artifacts == ("data/observations.csv",)


@pytest.mark.parametrize(
    "inputs",
    [
        "data/observations.csv",
        {"root": ".", "artifacts": "data/observations.csv"},
        {"root": "/absolute/root", "artifacts": ["data.csv"]},
        {"root": ".", "artifacts": ["/absolute/data.csv"]},
        {"root": ".", "artifacts": ["../outside.csv"]},
        {"root": ".", "artifacts": ["data.csv", "data.csv"]},
    ],
)
def test_scenario_schema_rejects_invalid_declared_inputs(
    inputs,
) -> None:
    with pytest.raises(ScenarioValidationError):
        ScenarioSchemaV1.from_mapping(
            {
                "schema_version": "abmforge.scenario.v1",
                "model": "example.Model",
                "run": {
                    "steps": 10,
                },
                "inputs": inputs,
            }
        )


def test_from_yaml_resolves_inputs_and_binds_them_to_v3(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module_path = _write(
        tmp_path / "yaml_input_model.py",
        ("from abmforge.core.model import Model\n\nclass YamlInputModel(Model):\n    pass\n"),
    )
    assert module_path.exists()

    monkeypatch.syspath_prepend(str(tmp_path))

    study_root = tmp_path / "study"
    input_path = _write(
        study_root / "data" / "observations.csv",
        "value\n1\n",
    )

    scenario_path = study_root / "configs" / "scenario.yaml"
    scenario_path.parent.mkdir(parents=True)

    scenario_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": "abmforge.scenario.v1",
                "model": "yaml_input_model.YamlInputModel",
                "run": {
                    "seed": 42,
                    "steps": 0,
                },
                "inputs": {
                    "root": "..",
                    "artifacts": [
                        "data/observations.csv",
                    ],
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    scenario = Scenario.from_yaml(scenario_path)

    assert scenario.input_root == study_root.resolve()
    assert tuple(scenario.input_artifacts) == (input_path.resolve(),)

    first = scenario.execution_fingerprint()

    assert first.schema_version == "execution-fingerprint-v3"
    assert first.input_artifact_count == 1

    input_path.write_bytes(b"value\n2\n")

    second = scenario.execution_fingerprint()

    assert first.input_artifacts_sha256 != second.input_artifacts_sha256
    assert first.digest != second.digest
