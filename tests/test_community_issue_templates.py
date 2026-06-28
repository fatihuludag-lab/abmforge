from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISSUE_TEMPLATE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"


def test_issue_templates_exist() -> None:
    expected = [
        "bug_report.yml",
        "feature_request.yml",
        "reproducibility_report.yml",
        "config.yml",
    ]

    for filename in expected:
        assert (ISSUE_TEMPLATE_DIR / filename).is_file(), filename


def test_bug_report_template_requests_reproducible_context() -> None:
    text = (ISSUE_TEMPLATE_DIR / "bug_report.yml").read_text(encoding="utf-8")

    required_terms = [
        "Minimal reproducible example",
        "Actual behavior and traceback",
        "ABMForge version",
        "Python version",
        "Operating system",
        "Installation method",
    ]

    for term in required_terms:
        assert term in text


def test_reproducibility_template_covers_archive_manifest_and_seed_context() -> None:
    text = (ISSUE_TEMPLATE_DIR / "reproducibility_report.yml").read_text(encoding="utf-8")

    required_terms = [
        "Archive structure or validation output",
        "Manifest / checksum details",
        "Seed or seed sequence",
        "abmforge validate",
        "manifest.json",
        "checksum",
    ]

    for term in required_terms:
        assert term in text


def test_support_and_contributing_docs_reference_issue_templates() -> None:
    support = (ROOT / "SUPPORT.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "bug report" in support.lower()
    assert "reproducibility report" in support.lower()
    assert "GitHub Issues" in support
    assert "issue templates" in contributing.lower()
    assert "reproducibility report" in contributing.lower()


def test_community_guidance_doc_is_linked_from_docs_nav() -> None:
    doc = (ROOT / "docs" / "community-and-issues.md").read_text(encoding="utf-8")
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Community and Issue Reporting" in doc
    assert "reproducibility report" in doc
    assert "community-and-issues.md" in mkdocs
