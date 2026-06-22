from pathlib import Path


def test_architecture_overview_doc_exists_and_covers_main_modules() -> None:
    text = Path("docs/architecture-overview.md").read_text(encoding="utf-8")

    expected_terms = [
        "core",
        "world",
        "time",
        "scheduling",
        "data",
        "experiment",
        "analysis",
        "methods",
        "repro",
        "cli",
    ]

    for term in expected_terms:
        assert f"`abmforge.{term}`" in text


def test_architecture_overview_documents_execution_flow() -> None:
    text = Path("docs/architecture-overview.md").read_text(encoding="utf-8")

    expected_phrases = [
        "Scenario YAML / Scenario",
        "Model construction",
        "Scheduler / World / Agents",
        "Recorder / Dataset",
        "Experiment archive",
        "Validate / Summarize / Analyze",
    ]

    for phrase in expected_phrases:
        assert phrase in text


def test_architecture_overview_documents_alpha_boundaries() -> None:
    text = Path("docs/architecture-overview.md").read_text(encoding="utf-8")

    expected_phrases = [
        "alpha-stage",
        "not yet be presented as a mature",
        "fully self-contained reconstruction system",
        "large-scale distributed execution is outside the current core scope",
    ]

    for phrase in expected_phrases:
        assert phrase in text


def test_architecture_overview_is_in_mkdocs_nav() -> None:
    text = Path("mkdocs.yml").read_text(encoding="utf-8")

    assert "Architecture Overview: architecture-overview.md" in text
