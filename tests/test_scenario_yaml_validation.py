from __future__ import annotations

import pytest

from abmforge.core.model import Model
from abmforge.experiment.scenario import Scenario


class ScenarioValidationModel(Model):
    def step(self) -> None:
        pass


def test_scenario_yaml_rejects_non_mapping_document(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
- invalid
- scenario
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Scenario YAML document must be a mapping"):
        Scenario.from_yaml(scenario_file)


def test_scenario_yaml_requires_model_field(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
name: missing_model
run:
  steps: 1
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required field: model"):
        Scenario.from_yaml(scenario_file)


def test_scenario_yaml_requires_model_to_be_string(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model:
  path: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  steps: 1
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Field 'model' must be a string"):
        Scenario.from_yaml(scenario_file)


def test_scenario_yaml_requires_parameters_to_be_mapping(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
parameters:
  - invalid
run:
  steps: 1
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Field 'parameters' must be a mapping"):
        Scenario.from_yaml(scenario_file)


def test_scenario_yaml_requires_run_to_be_mapping(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  - invalid
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Field 'run' must be a mapping"):
        Scenario.from_yaml(scenario_file)


def test_scenario_yaml_requires_steps_field(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  seed: 42
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required field: run.steps"):
        Scenario.from_yaml(scenario_file)


def test_scenario_yaml_rejects_non_integer_steps(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  steps: invalid
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Field 'run.steps' must be an integer"):
        Scenario.from_yaml(scenario_file)


def test_scenario_yaml_rejects_negative_steps(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  steps: -1
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Field 'run.steps' must be non-negative"):
        Scenario.from_yaml(scenario_file)


def test_scenario_yaml_rejects_non_integer_seed(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  seed: invalid
  steps: 1
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Field 'run.seed' must be an integer or null"):
        Scenario.from_yaml(scenario_file)


def test_scenario_yaml_accepts_valid_minimal_scenario(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
name: valid_scenario
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
parameters:
  value: 1
run:
  seed: 42
  steps: 1
""",
        encoding="utf-8",
    )

    scenario = Scenario.from_yaml(scenario_file)

    assert scenario.name == "valid_scenario"
    assert scenario.model.__name__ == "ScenarioValidationModel"
    assert issubclass(scenario.model, Model)
    assert scenario.parameters == {"value": 1}
    assert scenario.seed == 42
    assert scenario.steps == 1
