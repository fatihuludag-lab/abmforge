from pathlib import Path


def test_archive_format_docs_include_core_archive_layout() -> None:
    text = Path("docs/archive-format.md").read_text(encoding="utf-8")

    assert "configs/scenario.yaml" in text
    assert "manifest.json" in text
    assert "dataset_schema.json" in text
    assert "runs.json" in text
    assert "run_summary.json" in text


def test_archive_format_docs_include_cli_workflow() -> None:
    text = Path("docs/archive-format.md").read_text(encoding="utf-8")

    assert "abmforge run" in text
    assert "abmforge validate" in text
    assert "abmforge summarize" in text
    assert "Archive validation passed" in text


def test_archive_format_docs_explain_reproducibility_role() -> None:
    text = Path("docs/archive-format.md").read_text(encoding="utf-8")

    assert "Scenario YAML" in text
    assert "Dataset tables" in text
    assert "Dataset schema" in text
    assert "Manifest" in text
