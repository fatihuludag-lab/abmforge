from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "experiment-archive-v1.md"
MKDOCS = ROOT / "mkdocs.yml"


def test_experiment_archive_v1_spec_exists() -> None:
    assert SPEC.exists(), "docs/experiment-archive-v1.md should define the v1 archive contract"


def test_experiment_archive_v1_spec_mentions_required_contract_parts() -> None:
    text = SPEC.read_text(encoding="utf-8")

    required_terms = [
        "manifest.json",
        "dataset_schema.json",
        "run_index.json",
        "configs/",
        "data/",
        "reports/",
        "logs/",
        "snapshots/",
        "artifacts/",
        "runs.json",
        "model_records.jsonl",
        "agent_records.jsonl",
        "event_records.jsonl",
        "lifecycle_records.jsonl",
        "errors.jsonl",
        "Validation Requirements",
        "Compatibility Rules",
        "Non-Goals for v1",
        "archive_v1_contract",
        "required_directories",
        "required_top_level_files",
        "legacy_optional_top_level_files",
        "json_dataset_files",
        "parquet_dataset_files",
    ]

    for term in required_terms:
        assert term in text


def test_experiment_archive_v1_spec_is_listed_in_mkdocs_nav() -> None:
    nav = MKDOCS.read_text(encoding="utf-8")

    assert "Experiment Archive Specification v1" in nav
    assert "experiment-archive-v1.md" in nav
