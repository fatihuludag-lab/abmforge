from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_api_stability_policy_document_exists() -> None:
    path = ROOT / "docs" / "api-stability.md"
    assert path.exists(), "docs/api-stability.md should define API stability policy"


def test_api_stability_policy_defines_stability_levels() -> None:
    text = (ROOT / "docs" / "api-stability.md").read_text(encoding="utf-8")

    for term in [
        "Stable",
        "Provisional",
        "Experimental",
        "Deprecation Policy",
        "Breaking Changes",
        "Archive and Dataset Compatibility",
        "CLI Stability",
    ]:
        assert term in text


def test_api_stability_policy_covers_research_reproducibility() -> None:
    text = (ROOT / "docs" / "api-stability.md").read_text(encoding="utf-8")

    for term in [
        "ABMForge version",
        "Python version",
        "scenario or experiment configuration",
        "archive manifest",
        "dataset schema version",
    ]:
        assert term in text


def test_api_stability_policy_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "API Stability" in nav
    assert "api-stability.md" in nav
