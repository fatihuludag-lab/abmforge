from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "archive-migration-strategy.md"


def test_archive_migration_strategy_doc_exists() -> None:
    assert DOC.exists(), "docs/archive-migration-strategy.md should exist"


def test_archive_migration_strategy_names_current_format_and_goals() -> None:
    text = DOC.read_text(encoding="utf-8")

    expected_terms = [
        "experiment-archive-v1",
        "research artifacts",
        "avoid silent data reinterpretation",
        "fail clearly",
        "unsupported versions",
        "migration guidance",
    ]

    for term in expected_terms:
        assert term in text


def test_archive_migration_strategy_defines_compatibility_classes() -> None:
    text = DOC.read_text(encoding="utf-8")

    for term in [
        "Compatible Additions",
        "Soft-Breaking Changes",
        "Breaking Changes",
        "Reader Behavior",
        "Migration Principles",
        "Lossy Migration",
    ]:
        assert term in text


def test_archive_migration_strategy_includes_future_cli_shape() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "abmforge archive migrate" in text
    assert "--dry-run" in text
    assert "--report migration_report.json" in text
    assert "This PR documents the strategy only" in text


def test_archive_migration_strategy_has_developer_checklist() -> None:
    text = DOC.read_text(encoding="utf-8")

    for term in [
        "required files",
        "required table names",
        "required column names",
        "field semantics",
        "validation behavior",
        "new archive format version",
        "old fixture archives",
    ]:
        assert term in text


def test_archive_migration_strategy_is_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Archive Migration Strategy" in nav
    assert "archive-migration-strategy.md" in nav
