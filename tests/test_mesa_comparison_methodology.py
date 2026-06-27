from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "mesa-comparison-methodology.md"
BENCH_README = ROOT / "benchmarks" / "mesa" / "README.md"


def test_mesa_comparison_methodology_doc_exists() -> None:
    assert DOC.exists(), "docs/mesa-comparison-methodology.md should exist"


def test_mesa_comparison_methodology_is_conservative() -> None:
    text = DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    for term in [
        "methodology document, not a performance claim",
        "should not claim that it is a replacement for Mesa",
        "Do not claim that ABMForge is",
        "Any future performance claim should be backed",
        "not from memory",
    ]:
        assert term in normalized


def test_mesa_comparison_methodology_covers_research_artifacts() -> None:
    text = DOC.read_text(encoding="utf-8")

    for term in [
        "validated archive artifacts",
        "dataset schema",
        "run index",
        "manifest or provenance metadata",
        "analysis-ready tables",
        "robustness across seeds",
        "reproducibility metadata completeness",
    ]:
        assert term in text


def test_mesa_comparison_methodology_defines_benchmark_dimensions() -> None:
    text = DOC.read_text(encoding="utf-8")

    for term in [
        "model construction time",
        "run time without output writing",
        "run time with output writing",
        "validation time",
        "output directory size",
        "memory use",
    ]:
        assert term in text


def test_mesa_benchmark_readme_exists_but_does_not_add_dependency() -> None:
    text = BENCH_README.read_text(encoding="utf-8")

    assert "methodology only" in text
    assert "does not add Mesa as a dependency" in text
    assert "does not run Mesa benchmarks in CI" in text
    assert "equivalent model code" in text


def test_mesa_comparison_methodology_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Mesa Comparison Methodology" in nav
    assert "mesa-comparison-methodology.md" in nav
