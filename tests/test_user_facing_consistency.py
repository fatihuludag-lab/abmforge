from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_uses_reproducibility_oriented_positioning() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "reproducibility-oriented" in readme.lower()
    assert "**Reproducible by default**" not in readme
    assert "source code, inputs, and environments" in readme


def test_odd_export_docs_use_current_public_api() -> None:
    text = (ROOT / "docs" / "odd-export.md").read_text(encoding="utf-8")

    assert "from abmforge import Model, ODDDocument" in text
    assert "ODDDocument.from_model" in text
    assert "write_markdown" in text
    assert "write_json" in text
    assert "abmforge.export" not in text
    assert "model.to_odd" not in text


def test_roadmap_mentions_unified_archive_next_step() -> None:
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")

    assert "alpha-stage research software project" in roadmap
    assert "Unify single-run and multi-run experiment outputs" in roadmap
    assert "Experiment Archive Specification v1" in roadmap
