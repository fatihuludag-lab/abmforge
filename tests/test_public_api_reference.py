from __future__ import annotations

from pathlib import Path

import abmforge

ROOT = Path(__file__).resolve().parents[1]
API_DOC = ROOT / "docs" / "api.md"


def test_api_reference_mentions_all_root_public_exports() -> None:
    text = API_DOC.read_text(encoding="utf-8")

    missing = [name for name in abmforge.__all__ if f"`{name}`" not in text]

    assert not missing, "Missing public API docs for: " + ", ".join(missing)


def test_api_reference_defines_stability_labels() -> None:
    text = API_DOC.read_text(encoding="utf-8")

    for label in ["Stable", "Provisional", "Experimental", "Internal"]:
        assert label in text


def test_api_reference_includes_core_user_workflow_symbols() -> None:
    text = API_DOC.read_text(encoding="utf-8")

    for symbol in [
        "Agent",
        "Model",
        "Scenario",
        "Experiment",
        "Dataset",
        "Recorder",
        "ExperimentArchive",
        "ODDDocument",
    ]:
        assert f"### `{symbol}`" in text


def test_api_reference_warns_that_abmforge_is_alpha() -> None:
    text = API_DOC.read_text(encoding="utf-8").lower()

    assert "alpha" in text
    assert "provisional" in text
    assert "api stability policy" in text


def test_api_reference_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "API Reference" in nav
    assert "api.md" in nav
