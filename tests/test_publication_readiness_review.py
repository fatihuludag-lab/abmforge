from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_publication_readiness_review_doc_exists() -> None:
    assert (ROOT / "docs" / "publication-readiness-review.md").is_file()


def test_publication_readiness_review_declares_status_and_blockers() -> None:
    doc = (ROOT / "docs" / "publication-readiness-review.md").read_text(encoding="utf-8")

    required_terms = [
        "publication-oriented research-workflow alpha",
        "Submission blockers",
        "Public alpha release",
        "Install smoke from published artifact",
        "Release artifact and DOI",
        "Final paper review",
        "Manual ODD review",
        "Repository issue settings",
    ]

    for term in required_terms:
        assert term in doc


def test_publication_readiness_review_qualifies_claims() -> None:
    doc = (ROOT / "docs" / "publication-readiness-review.md").read_text(encoding="utf-8")

    required_terms = [
        "Claims that are currently defensible",
        "Claims to avoid or qualify",
        "replaces Mesa, NetLogo, Repast, MASON, or Agents.jl",
        "full deterministic replay",
        "production-ready",
        "available from PyPI unless the release has actually happened",
    ]

    for term in required_terms:
        assert term in doc


def test_publication_readiness_review_has_reviewer_risk_register() -> None:
    doc = (ROOT / "docs" / "publication-readiness-review.md").read_text(encoding="utf-8")

    required_terms = [
        "Reviewer risk register",
        "Alpha API",
        "Release status",
        "Reproducibility scope",
        "Differentiation",
        "Community support",
    ]

    for term in required_terms:
        assert term in doc


def test_publication_readiness_review_is_linked_from_docs_nav() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "publication-readiness-review.md" in mkdocs
