from pathlib import Path


def test_scenario_yaml_reference_documents_required_fields() -> None:
    text = Path("docs/scenario-yaml.md").read_text(encoding="utf-8")

    assert "`model`" in text
    assert "`run.steps`" in text
    assert "Missing required field: model" in text
    assert "Missing required field: run.steps" in text


def test_scenario_yaml_reference_documents_cli_workflow() -> None:
    text = Path("docs/scenario-yaml.md").read_text(encoding="utf-8")

    assert "abmforge run" in text
    assert "abmforge validate" in text
    assert "abmforge summarize" in text
    assert "Scenario validation failed:" in text


def test_scenario_yaml_reference_documents_schema_v1_contract() -> None:
    text = Path("docs/scenario-yaml.md").read_text(encoding="utf-8")

    assert "schema_version: abmforge.scenario.v1" in text
    assert "`schema_version` | yes" in text
    assert "Unknown scenario field" in text
    assert "Unknown run field" in text
    assert "`extensions`" in text
    assert "Migrating legacy Scenario YAML" in text


def test_experiment_yaml_is_documented_as_separate_contract() -> None:
    text = Path("docs/experiment-yaml.md").read_text(encoding="utf-8")

    assert "separate configuration contract from Scenario Schema V1" in text
    assert "Do not add `schema_version: abmforge.scenario.v1`" in text


def test_public_api_documents_scenario_schema_v1() -> None:
    text = Path("docs/api.md").read_text(encoding="utf-8")

    assert "SCENARIO_SCHEMA_VERSION" in text
    assert "ScenarioSchemaV1" in text
    assert "ScenarioValidationError" in text


def test_scenario_yaml_docs_document_declarative_stop_condition() -> None:
    from pathlib import Path

    text = Path("docs/scenario-yaml.md").read_text(encoding="utf-8")

    assert "## Declarative stop conditions" in text
    assert "stop:" in text
    assert "field: infected" in text
    assert "operator: le" in text
    assert "value: 0" in text

    for operator in ("`eq`", "`ne`", "`lt`", "`le`", "`gt`", "`ge`"):
        assert operator in text


def test_scenario_yaml_docs_document_stop_safety_contract() -> None:
    from pathlib import Path

    text = Path("docs/scenario-yaml.md").read_text(encoding="utf-8")

    assert "does not use `eval()`" in text
    assert "arbitrary Python" in text
    assert "Private names" in text
    assert "dotted traversal" in text
    assert "before the first step" in text
    assert "after each" in text
    assert "`stop_condition`" in text


def test_scenario_yaml_docs_document_stop_recovery_limitation() -> None:
    from pathlib import Path

    text = Path("docs/scenario-yaml.md").read_text(encoding="utf-8")

    assert "`execution-fingerprint-v3`" in text
    assert "fail-closed" in text
    assert "non-reusable" in text


def test_scenario_yaml_docs_document_declared_inputs() -> None:
    text = Path("docs/scenario-yaml.md").read_text(encoding="utf-8")

    assert "## Declared input artifacts" in text
    assert "inputs:" in text
    assert "root: .." in text
    assert "artifacts:" in text
    assert "`inputs.root`" in text
    assert "`inputs.artifacts`" in text
    assert "`DeclaredInputIdentityV1`" in text
    assert "`ExecutionFingerprintV3`" in text
    assert "not automatically discovered" in text
    assert "duplicate artifact paths are rejected" in text


def test_api_documents_scenario_yaml_declared_input_binding() -> None:
    text = Path("docs/api.md").read_text(encoding="utf-8")

    assert "`inputs.root`" in text
    assert "`inputs.artifacts`" in text
    assert "`input_root`" in text
    assert "`input_artifacts`" in text
    assert "`DeclaredInputIdentityV1`" in text
    assert "`ExecutionFingerprintV3`" in text


def test_experiment_yaml_excludes_scenario_inputs_contract() -> None:
    text = Path("docs/experiment-yaml.md").read_text(encoding="utf-8")

    assert "Scenario Schema V1 `inputs` block" in text
    assert "not an Experiment YAML field" in text
