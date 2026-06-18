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
