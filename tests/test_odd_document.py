from __future__ import annotations

import json

import pytest

from abmforge import Model, ODDDocument


class SimpleModel(Model):
    """Minimal model used for ODD document tests."""

    def setup(self) -> None:
        self.population = 0

    def step(self) -> None:
        self.population += 1


def test_odd_document_from_model_contains_core_sections() -> None:
    odd = ODDDocument.from_model(
        SimpleModel,
        purpose="Demonstrate ODD documentation generation.",
        authors=["Fatih Uludağ"],
        entities=["Person"],
        scales={"time": "step", "space": "abstract"},
        process_overview=["The model advances by one discrete step."],
        design_concepts={
            "stochasticity": "No stochasticity is used in this minimal example.",
        },
        initialization=["The model initializes a population counter."],
    )

    odd.add_state_variable(
        "Person",
        "wealth",
        description="Example agent-level state variable.",
        kind="float",
        unit="abstract units",
    )
    odd.add_input_data(
        name="none",
        description="This example does not use external input data.",
        source="n/a",
    )
    odd.add_submodel(
        name="population update",
        description="Increment a model-level counter.",
        source="SimpleModel.step",
    )

    data = odd.to_dict()

    assert data["schema_version"] == "abmforge.odd.v1"
    assert data["title"] == "ODD documentation for SimpleModel"
    assert data["purpose"] == "Demonstrate ODD documentation generation."
    assert data["model"]["name"] == "SimpleModel"
    assert data["model"]["module"] == __name__
    assert "setup" in data["model"]["public_methods"]
    assert "step" in data["model"]["public_methods"]
    assert data["authors"] == ["Fatih Uludağ"]
    assert data["entities"][0]["name"] == "Person"
    assert data["scales"]["time"] == "step"
    assert data["completeness"]["purpose"] is True
    assert data["manual_review_required"] is True


def test_odd_document_markdown_contains_odd_headings() -> None:
    odd = ODDDocument.from_model(
        SimpleModel,
        purpose="Test Markdown export.",
        entities=["Person"],
        scales={"time": "step"},
        process_overview=["Step the model."],
    )

    markdown = odd.to_markdown()

    assert "# ODD documentation for SimpleModel" in markdown
    assert "## 1. Purpose" in markdown
    assert "## 2. Entities, State Variables, and Scales" in markdown
    assert "## 3. Process Overview and Scheduling" in markdown
    assert "## 4. Design Concepts" in markdown
    assert "## 5. Initialization" in markdown
    assert "## 6. Input Data" in markdown
    assert "## 7. Submodels" in markdown
    assert "## 8. Decision Processes" in markdown
    assert "Manual review and completion are required" in markdown


def test_odd_document_write_markdown_and_json(tmp_path) -> None:  # type: ignore[no-untyped-def]
    odd = ODDDocument.from_model(
        SimpleModel,
        purpose="Test file writing.",
        entities=["Person"],
    )

    markdown_path = odd.write_markdown(tmp_path)
    json_path = odd.write_json(tmp_path)

    assert markdown_path.name == "ODD.md"
    assert markdown_path.exists()
    assert json_path.name == "ODD.json"
    assert json_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))

    assert data["schema_version"] == "abmforge.odd.v1"
    assert data["model"]["name"] == "SimpleModel"


def test_odd_document_custom_file_paths(tmp_path) -> None:  # type: ignore[no-untyped-def]
    odd = ODDDocument.from_model(SimpleModel, purpose="Test custom paths.")

    markdown_path = odd.write_markdown(tmp_path / "custom_odd.md")
    json_path = odd.write_json(tmp_path / "custom_odd.json")

    assert markdown_path.name == "custom_odd.md"
    assert json_path.name == "custom_odd.json"


def test_odd_document_rejects_empty_purpose() -> None:
    with pytest.raises(ValueError, match="purpose"):
        ODDDocument.from_model(SimpleModel, purpose="")


def test_odd_document_decision_processes_support_ai_agent_documentation() -> None:
    odd = ODDDocument.from_model(
        SimpleModel,
        purpose="Document an AI-agent decision process.",
    )

    odd.add_decision_process(
        name="evacuation decision",
        actor="Household AI agent",
        description="The agent decides whether to evacuate.",
        inputs=["risk", "income", "neighbour behaviour"],
        outputs=["evacuate", "reason"],
        notes="LLM use must be audited and replayable.",
    )

    data = odd.to_dict()

    assert data["decision_processes"][0]["name"] == "evacuation decision"
    assert data["decision_processes"][0]["actor"] == "Household AI agent"
    assert "risk" in data["decision_processes"][0]["inputs"]

    markdown = odd.to_markdown()

    assert "Household AI agent" in markdown
    assert "LLM use must be audited and replayable" in markdown
