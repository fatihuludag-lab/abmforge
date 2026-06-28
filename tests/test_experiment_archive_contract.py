from __future__ import annotations

from abmforge.experiment.archive import (
    ARCHIVE_FORMAT_VERSION,
    ExperimentArchive,
    archive_v1_contract,
)


def test_archive_v1_contract_declares_minimum_storage_surface() -> None:
    contract = archive_v1_contract()

    assert contract["archive_format"] == ARCHIVE_FORMAT_VERSION
    assert contract["supported_archive_formats"] == [ARCHIVE_FORMAT_VERSION]
    assert set(contract["required_directories"]) == {
        "configs",
        "data",
        "reports",
        "logs",
        "snapshots",
    }
    assert contract["optional_directories"] == ["artifacts"]
    assert contract["required_top_level_files"] == [
        "manifest.json",
        "dataset_schema.json",
    ]
    assert contract["legacy_optional_top_level_files"] == [
        "run_index.json",
        "registry.json",
    ]
    assert set(contract["json_dataset_files"]) == {
        "runs",
        "model_records",
        "agent_records",
        "event_records",
        "lifecycle_records",
        "errors",
    }
    assert set(contract["parquet_dataset_files"]) == set(contract["json_dataset_files"])


def test_archive_create_matches_declared_required_directories(tmp_path) -> None:
    archive = ExperimentArchive.create(tmp_path / "archive")
    contract = archive_v1_contract()

    for directory in contract["required_directories"]:
        assert (archive.path / directory).is_dir(), directory


def test_archive_validate_uses_declared_required_top_level_files(tmp_path) -> None:
    archive = ExperimentArchive.create(tmp_path / "archive")

    errors = archive.validate()

    for filename in archive_v1_contract()["required_top_level_files"]:
        assert f"Missing {filename}" in errors
