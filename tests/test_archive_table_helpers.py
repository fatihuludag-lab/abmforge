from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from abmforge.analysis import load_archive_table, load_archive_tables
from abmforge.analysis.archive_tables import (
    STANDARD_ARCHIVE_TABLES,
    ArchiveTableError,
    list_archive_tables,
)

ROOT = Path(__file__).resolve().parents[1]


def _write_archive_tables(archive: Path) -> None:
    data_dir = archive / "data"
    data_dir.mkdir(parents=True)

    (data_dir / "runs.json").write_text(
        json.dumps(
            [
                {
                    "run_id": "run-1",
                    "status": "completed",
                    "steps": 3,
                }
            ]
        ),
        encoding="utf-8",
    )

    (data_dir / "model_records.csv").write_text(
        "run_id,step,metric,value\nrun-1,0,adoption_share,0.1\nrun-1,1,adoption_share,0.2\n",
        encoding="utf-8",
    )

    (data_dir / "agent_records.jsonl").write_text(
        '{"run_id": "run-1", "step": 0, "agent_id": 1, "variable": "state"}\n'
        '{"run_id": "run-1", "step": 1, "agent_id": 1, "variable": "state"}\n',
        encoding="utf-8",
    )


def test_standard_archive_tables_include_core_tables() -> None:
    for table in ["runs", "model_records", "agent_records", "errors"]:
        assert table in STANDARD_ARCHIVE_TABLES


def test_list_archive_tables_detects_supported_files(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _write_archive_tables(archive)

    tables = list_archive_tables(archive)

    assert set(tables) == {"runs", "model_records", "agent_records"}
    assert tables["runs"].name == "runs.json"
    assert tables["model_records"].name == "model_records.csv"


def test_load_archive_table_reads_json_csv_and_jsonl(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _write_archive_tables(archive)

    runs = load_archive_table(archive, "runs")
    model_records = load_archive_table(archive, "model_records")
    agent_records = load_archive_table(archive, "agent_records.jsonl")

    assert runs == [{"run_id": "run-1", "status": "completed", "steps": 3}]
    assert model_records[0]["metric"] == "adoption_share"
    assert model_records[1]["value"] == "0.2"
    assert len(agent_records) == 2


def test_load_archive_tables_loads_detected_tables(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _write_archive_tables(archive)

    tables = load_archive_tables(archive)

    assert set(tables) == {"runs", "model_records", "agent_records"}
    assert len(tables["runs"]) == 1


def test_load_archive_tables_can_ignore_missing_explicit_tables(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _write_archive_tables(archive)

    tables = load_archive_tables(
        archive,
        tables=["runs", "missing_table"],
        missing="ignore",
    )

    assert set(tables) == {"runs"}


def test_load_archive_table_raises_clear_error_for_missing_table(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _write_archive_tables(archive)

    with pytest.raises(ArchiveTableError, match="missing_table"):
        load_archive_table(archive, "missing_table")


def test_load_archive_table_can_return_pandas_dataframe_if_available(
    tmp_path: Path,
) -> None:
    if importlib.util.find_spec("pandas") is None:
        pytest.skip("pandas is not installed")

    archive = tmp_path / "archive"
    _write_archive_tables(archive)

    dataframe = load_archive_table(archive, "model_records", as_dataframe=True)

    assert list(dataframe.columns) == ["run_id", "step", "metric", "value"]
    assert len(dataframe) == 2


def test_archive_table_analysis_docs_are_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Archive Table Analysis" in nav
    assert "archive-table-analysis.md" in nav
