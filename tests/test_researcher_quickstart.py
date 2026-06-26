from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "researcher-quickstart.md"


def test_researcher_quickstart_exists() -> None:
    assert DOC.exists(), "docs/researcher-quickstart.md should exist"


def test_researcher_quickstart_covers_end_to_end_workflow() -> None:
    text = DOC.read_text(encoding="utf-8")

    expected_terms = [
        "Researcher Quickstart",
        "python -m pip install -e",
        "abmforge --version",
        "abmforge info",
        "abmforge run examples/scenarios/wealth_baseline.yaml",
        "abmforge validate outputs/wealth_baseline_archive",
        "abmforge summarize outputs/wealth_baseline_archive",
        "python examples/reproducible_study/reproduce.py",
        "manifest.json",
        "dataset_schema.json",
        "run_index.json",
    ]

    for term in expected_terms:
        assert term in text


def test_researcher_quickstart_is_careful_about_alpha_release_status() -> None:
    text = DOC.read_text(encoding="utf-8").lower()

    assert "alpha-stage research software" in text
    assert "when a release is available from pypi" in text
    assert "pin the exact" in text
    assert "valid archive" in text
    assert "scientifically valid" in text


def test_researcher_quickstart_avoids_placeholder_model_language() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "MyModel" not in text
    assert "TODO" not in text


def test_researcher_quickstart_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Researcher Quickstart" in nav
    assert "researcher-quickstart.md" in nav
