from __future__ import annotations

import pytest

from abmforge.experiment.scenario_schema import (
    SCENARIO_SCHEMA_VERSION,
    ScenarioSchemaV1,
    ScenarioValidationError,
)


def test_scenario_schema_v1_normalizes_valid_document() -> None:
    schema = ScenarioSchemaV1.from_mapping(
        {
            "schema_version": SCENARIO_SCHEMA_VERSION,
            "name": "baseline",
            "model": "package.module.Model",
            "parameters": {"n": 100},
            "run": {"seed": 42, "steps": 10},
            "extensions": {
                "example.plugin": {
                    "mode": "strict",
                }
            },
        }
    )

    assert schema.schema_version == "abmforge.scenario.v1"
    assert schema.name == "baseline"
    assert schema.model == "package.module.Model"
    assert schema.parameters == {"n": 100}
    assert schema.seed == 42
    assert schema.steps == 10
    assert schema.extensions == {
        "example.plugin": {
            "mode": "strict",
        }
    }


def test_scenario_schema_v1_rejects_non_mapping_extensions() -> None:
    with pytest.raises(
        ScenarioValidationError,
        match="Field 'extensions' must be a mapping/object",
    ):
        ScenarioSchemaV1.from_mapping(
            {
                "schema_version": SCENARIO_SCHEMA_VERSION,
                "model": "package.module.Model",
                "run": {"steps": 1},
                "extensions": ["invalid"],
            }
        )


def test_scenario_schema_v1_allows_arbitrary_namespaced_extension_payloads() -> None:
    schema = ScenarioSchemaV1.from_mapping(
        {
            "schema_version": SCENARIO_SCHEMA_VERSION,
            "model": "package.module.Model",
            "run": {"steps": 1},
            "extensions": {
                "org.example.plugin": {
                    "arbitrary": {
                        "nested": [1, 2, 3],
                    }
                }
            },
        }
    )

    assert schema.extensions["org.example.plugin"]["arbitrary"] == {
        "nested": [1, 2, 3],
    }


def test_scenario_yaml_and_python_api_are_semantically_equivalent(
    tmp_path,
) -> None:
    from tests.test_scenario_yaml_validation import (
        ScenarioValidationModel,
    )

    from abmforge.experiment import Scenario

    yaml_path = tmp_path / "scenario.yaml"
    yaml_path.write_text(
        """
schema_version: abmforge.scenario.v1
name: semantic-equivalence
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
parameters:
  value: 7
run:
  seed: 123
  steps: 4
extensions:
  org.example.test:
    mode: strict
""".lstrip(),
        encoding="utf-8",
    )

    from_yaml = Scenario.from_yaml(yaml_path)

    from_python = Scenario(
        model=ScenarioValidationModel,
        parameters={"value": 7},
        seed=123,
        steps=4,
        name="semantic-equivalence",
        schema_version="abmforge.scenario.v1",
        extensions={
            "org.example.test": {
                "mode": "strict",
            }
        },
    )

    assert from_yaml.model is from_python.model
    assert from_yaml.parameters == from_python.parameters
    assert from_yaml.seed == from_python.seed
    assert from_yaml.steps == from_python.steps
    assert from_yaml.name == from_python.name
    assert from_yaml.schema_version == from_python.schema_version
    assert from_yaml.extensions == from_python.extensions

    assert from_yaml.execution_fingerprint().digest == from_python.execution_fingerprint().digest


def test_scenario_schema_v1_accepts_declarative_stop_condition() -> None:
    schema = ScenarioSchemaV1.from_mapping(
        {
            "schema_version": SCENARIO_SCHEMA_VERSION,
            "model": "package.module.Model",
            "run": {
                "steps": 10,
                "stop": {
                    "field": "steps",
                    "operator": "ge",
                    "value": 1,
                },
            },
        }
    )

    assert schema.stop is not None
    assert schema.stop.field == "steps"
    assert schema.stop.operator == "ge"
    assert schema.stop.value == 1


def test_scenario_schema_v1_rejects_unsupported_stop_operator() -> None:
    with pytest.raises(
        ScenarioValidationError,
        match="Unsupported stop operator",
    ):
        ScenarioSchemaV1.from_mapping(
            {
                "schema_version": SCENARIO_SCHEMA_VERSION,
                "model": "package.module.Model",
                "run": {
                    "steps": 10,
                    "stop": {
                        "field": "steps",
                        "operator": "approximately",
                        "value": 1,
                    },
                },
            }
        )


def test_scenario_schema_v1_rejects_private_stop_field() -> None:
    with pytest.raises(
        ScenarioValidationError,
        match="public model attribute name",
    ):
        ScenarioSchemaV1.from_mapping(
            {
                "schema_version": SCENARIO_SCHEMA_VERSION,
                "model": "package.module.Model",
                "run": {
                    "steps": 10,
                    "stop": {
                        "field": "_internal_state",
                        "operator": "eq",
                        "value": 0,
                    },
                },
            }
        )


def test_scenario_schema_v1_rejects_non_mapping_stop() -> None:
    with pytest.raises(
        ScenarioValidationError,
        match="Field 'run.stop' must be a mapping/object",
    ):
        ScenarioSchemaV1.from_mapping(
            {
                "schema_version": SCENARIO_SCHEMA_VERSION,
                "model": "package.module.Model",
                "run": {
                    "steps": 10,
                    "stop": ["invalid"],
                },
            }
        )


def test_scenario_schema_v1_rejects_unknown_stop_field() -> None:
    with pytest.raises(
        ScenarioValidationError,
        match="Unknown stop field",
    ):
        ScenarioSchemaV1.from_mapping(
            {
                "schema_version": SCENARIO_SCHEMA_VERSION,
                "model": "package.module.Model",
                "run": {
                    "steps": 10,
                    "stop": {
                        "field": "steps",
                        "operator": "ge",
                        "value": 1,
                        "unexpected": True,
                    },
                },
            }
        )


def test_scenario_schema_v1_requires_stop_operator() -> None:
    with pytest.raises(
        ScenarioValidationError,
        match="Missing required field: run.stop.operator",
    ):
        ScenarioSchemaV1.from_mapping(
            {
                "schema_version": SCENARIO_SCHEMA_VERSION,
                "model": "package.module.Model",
                "run": {
                    "steps": 10,
                    "stop": {
                        "field": "steps",
                        "value": 1,
                    },
                },
            }
        )


def test_scenario_schema_v1_rejects_non_scalar_stop_value() -> None:
    with pytest.raises(
        ScenarioValidationError,
        match="Field 'run.stop.value' must be a scalar value",
    ):
        ScenarioSchemaV1.from_mapping(
            {
                "schema_version": SCENARIO_SCHEMA_VERSION,
                "model": "package.module.Model",
                "run": {
                    "steps": 10,
                    "stop": {
                        "field": "steps",
                        "operator": "ge",
                        "value": [1, 2],
                    },
                },
            }
        )


def test_scenario_schema_v1_rejects_dotted_stop_field() -> None:
    with pytest.raises(
        ScenarioValidationError,
        match="public model attribute name",
    ):
        ScenarioSchemaV1.from_mapping(
            {
                "schema_version": SCENARIO_SCHEMA_VERSION,
                "model": "package.module.Model",
                "run": {
                    "steps": 10,
                    "stop": {
                        "field": "state.steps",
                        "operator": "ge",
                        "value": 1,
                    },
                },
            }
        )


@pytest.mark.parametrize(
    ("operator", "target"),
    [
        ("eq", 5),
        ("ne", 4),
        ("lt", 6),
        ("le", 5),
        ("gt", 4),
        ("ge", 5),
    ],
)
def test_scenario_schema_v1_stop_operators_execute(
    operator: str,
    target: int,
) -> None:
    schema = ScenarioSchemaV1.from_mapping(
        {
            "schema_version": SCENARIO_SCHEMA_VERSION,
            "model": "package.module.Model",
            "run": {
                "steps": 10,
                "stop": {
                    "field": "steps",
                    "operator": operator,
                    "value": target,
                },
            },
        }
    )

    class ObservedModel:
        steps = 5

    assert schema.stop is not None
    assert schema.stop.evaluate(ObservedModel()) is True
