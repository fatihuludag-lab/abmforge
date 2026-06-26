from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_community_health_root_files_exist() -> None:
    required_files = [
        "SECURITY.md",
        "SUPPORT.md",
        "GOVERNANCE.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
    ]

    for rel_path in required_files:
        assert (ROOT / rel_path).exists(), f"Missing {rel_path}"


def test_issue_templates_exist() -> None:
    required_templates = [
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/ISSUE_TEMPLATE/documentation.yml",
        ".github/ISSUE_TEMPLATE/model_zoo_proposal.yml",
        ".github/ISSUE_TEMPLATE/rfc.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
    ]

    for rel_path in required_templates:
        path = ROOT / rel_path
        assert path.exists(), f"Missing {rel_path}"
        text = path.read_text(encoding="utf-8")
        assert "name:" in text
        assert "body:" in text or "blank_issues_enabled:" in text


def test_security_policy_sets_alpha_expectations() -> None:
    text = (ROOT / "SECURITY.md").read_text(encoding="utf-8")

    assert "alpha-stage research software project" in text
    assert "Reporting a Vulnerability" in text
    assert "safe execution of untrusted model code" in text


def test_pull_request_template_mentions_quality_gates() -> None:
    text = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")

    assert "python -m ruff check" in text
    assert "python -m pytest -q" in text
    assert "python -m mypy src" in text
    assert "python -m mkdocs build --strict" in text
    assert "archive validation" in text.lower()
