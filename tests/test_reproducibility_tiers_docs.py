from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "reproducibility-tiers.md"


def test_reproducibility_tiers_doc_exists() -> None:
    assert DOC_PATH.exists()


def test_reproducibility_tiers_doc_is_in_mkdocs_nav() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "reproducibility-tiers.md" in mkdocs


def test_reproducibility_tiers_define_expected_levels() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Tier 0",
        "Tier 1",
        "Tier 2",
        "Tier 3",
        "Tier 4",
        "Tier 5",
        "Tier 6",
        "Same-Code Seeded Run Reproducibility",
        "Archive Integrity Reproducibility",
        "Independent Reconstruction",
    ]:
        assert phrase in text


def test_reproducibility_tiers_state_current_limits() -> None:
    text = DOC_PATH.read_text(encoding="utf-8").lower()

    assert "does not yet guarantee full independent reproduction" in text
    assert "does not currently guarantee byte-identical artifacts" in text
    assert "snapshot-related helpers" in text
    assert "experimental" in text


def test_reproducibility_tiers_recommend_preserving_external_context() -> None:
    text = DOC_PATH.read_text(encoding="utf-8").lower()

    for phrase in [
        "model source code",
        "input data",
        "dependency lock",
        "environment exports",
        "abmforge version or commit hash",
    ]:
        assert phrase in text
