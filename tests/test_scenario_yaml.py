from __future__ import annotations

import pytest

from abmforge.core.model import Model
from abmforge.experiment.scenario import Scenario


class YamlTestModel(Model):
    def setup(self) -> None:
        self.value = self.parameters.get("value", 0)

    def step(self) -> None:
        self.record.dataset.record_model(
            step=self.steps,
            time=float(self.time),
            metric="value",
            value=self.value,
        )


def test_scenario_from_yaml(tmp_path, monkeypatch):
    module_name = "tests.test_scenario_yaml.YamlTestModel"

    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        f"""
name: yaml_test
model: {module_name}

parameters:
  value: 7

run:
  seed: 123
  steps: 3
""",
        encoding="utf-8",
    )

    scenario = Scenario.from_yaml(scenario_file)

    assert scenario.name == "yaml_test"
    assert scenario.model.__name__ == "YamlTestModel"
    assert issubclass(scenario.model, Model)
    assert scenario.parameters == {"value": 7}
    assert scenario.seed == 123
    assert scenario.steps == 3

    result = scenario.run()

    assert result.status == "completed"
    assert result.steps == 3


def test_scenario_from_yaml_requires_model(tmp_path):
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
name: missing_model
run:
  steps: 1
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="model"):
        Scenario.from_yaml(scenario_file)


def test_scenario_from_yaml_rejects_invalid_parameters(tmp_path):
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model: tests.test_scenario_yaml.YamlTestModel
parameters:
  - invalid
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="parameters"):
        Scenario.from_yaml(scenario_file)


def test_scenario_from_yaml_rejects_invalid_steps(tmp_path):
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
model: tests.test_scenario_yaml.YamlTestModel
run:
  steps: invalid
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="steps"):
        Scenario.from_yaml(scenario_file)
