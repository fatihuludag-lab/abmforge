from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from abmforge.experiment.archive import ARCHIVE_FORMAT_VERSION, ExperimentArchive

ROOT = Path(__file__).resolve().parents[1]


def _write_minimal_archive(
    path: Path,
    *,
    archive_format: str | None,
) -> ExperimentArchive:
    archive = ExperimentArchive.create(path)

    manifest: dict[str, object] = {
        "dataset_schema_hash": "placeholder",
        "record_counts": {},
        "record_hashes": {},
    }
    if archive_format is not None:
        manifest["archive_format"] = archive_format

    archive.manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    archive.dataset_schema_path.write_text("{}", encoding="utf-8")
    (archive.data_dir / "runs.json").write_text("[]", encoding="utf-8")

    return archive


def test_archive_format_version_constant_is_current_v1() -> None:
    assert ARCHIVE_FORMAT_VERSION == "experiment-archive-v1"


def test_validate_reports_unsupported_archive_format_early(tmp_path: Path) -> None:
    archive = _write_minimal_archive(
        tmp_path / "archive",
        archive_format="experiment-archive-v999",
    )

    errors = archive.validate()

    assert errors
    assert errors[0].startswith("Unsupported archive format: experiment-archive-v999")
    assert "experiment-archive-v1" in errors[0]
    assert "archive-migration-strategy.md" in errors[0]


def test_validate_allows_legacy_archive_without_archive_format_key(
    tmp_path: Path,
) -> None:
    archive = _write_minimal_archive(tmp_path / "archive", archive_format=None)

    errors = archive.validate()

    assert not any("Unsupported archive format" in error for error in errors)


def test_cli_validate_reports_unsupported_archive_format(tmp_path: Path) -> None:
    archive = _write_minimal_archive(
        tmp_path / "archive",
        archive_format="experiment-archive-v999",
    )

    result = subprocess.run(
        [sys.executable, "-m", "abmforge.cli.main", "validate", str(archive.path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    output = result.stdout + result.stderr
    assert "Archive validation failed:" in output
    assert "Unsupported archive format: experiment-archive-v999" in output


def test_archive_migration_strategy_documents_validator_behavior() -> None:
    text = (ROOT / "docs" / "archive-migration-strategy.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Implemented Validator Behavior" in text
    assert "unsupported `archive_format`" in text
    assert "legacy alpha archives" in normalized
