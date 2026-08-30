from __future__ import annotations

import pytest

from abmforge.core.model import Model
from abmforge.experiment.scenario import Scenario, ScenarioValidationError


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
schema_version: abmforge.scenario.v1
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
schema_version: abmforge.scenario.v1
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
schema_version: abmforge.scenario.v1
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
schema_version: abmforge.scenario.v1
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
schema_version: abmforge.scenario.v1
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
schema_version: abmforge.scenario.v1
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
schema_version: abmforge.scenario.v1
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
schema_version: abmforge.scenario.v1
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
schema_version: abmforge.scenario.v1
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


def test_scenario_validation_error_includes_file_field_and_hint(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        "schema_version: abmforge.scenario.v1\nname: missing_model\nrun:\n  steps: 1\n",
        encoding="utf-8",
    )

    with pytest.raises(ScenarioValidationError) as exc_info:
        Scenario.from_yaml(scenario_file)

    message = str(exc_info.value)
    assert "Missing required field: model" in message
    assert f"file: {scenario_file}" in message
    assert "field: model" in message
    assert "Hint:" in message


def test_scenario_yaml_parse_errors_are_validation_errors(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text("model: [\n", encoding="utf-8")

    with pytest.raises(
        ScenarioValidationError,
        match="Scenario YAML could not be parsed",
    ) as exc_info:
        Scenario.from_yaml(scenario_file)

    message = str(exc_info.value)
    assert f"file: {scenario_file}" in message
    assert "Hint:" in message


def test_scenario_yaml_import_errors_are_validation_errors(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        (
            "schema_version: abmforge.scenario.v1\n"
            "model: missing_package.missing_module.MissingModel\n"
            "run:\n"
            "  steps: 1\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ScenarioValidationError) as exc_info:
        Scenario.from_yaml(scenario_file)

    message = str(exc_info.value)
    assert "field: model" in message
    assert "importable" in message
    assert f"file: {scenario_file}" in message


def test_scenario_yaml_requires_schema_version(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  steps: 1
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ScenarioValidationError,
        match="Missing required field: schema_version",
    ) as exc_info:
        Scenario.from_yaml(scenario_file)

    assert "field: schema_version" in str(exc_info.value)


def test_scenario_yaml_rejects_unsupported_schema_version(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
schema_version: abmforge.scenario.v999
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  steps: 1
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ScenarioValidationError,
        match="Unsupported scenario schema version",
    ) as exc_info:
        Scenario.from_yaml(scenario_file)

    assert "field: schema_version" in str(exc_info.value)
    assert "abmforge.scenario.v999" in str(exc_info.value)


def test_scenario_yaml_rejects_unknown_root_field(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
schema_version: abmforge.scenario.v1
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
unexpected: silently_ignored_before
run:
  steps: 1
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ScenarioValidationError,
        match="Unknown scenario field",
    ) as exc_info:
        Scenario.from_yaml(scenario_file)

    assert "unexpected" in str(exc_info.value)


def test_scenario_yaml_rejects_unknown_run_field(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
schema_version: abmforge.scenario.v1
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  steps: 1
  unexpected: silently_ignored_before
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ScenarioValidationError,
        match="Unknown run field",
    ) as exc_info:
        Scenario.from_yaml(scenario_file)

    assert "run.unexpected" in str(exc_info.value)
