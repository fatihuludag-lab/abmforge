from __future__ import annotations

from pathlib import Path

import pytest

from abmforge.experiment.archive_transaction import ArchiveTransaction


def _transaction_artifacts(parent: Path) -> list[Path]:
    return sorted(
        path for path in parent.iterdir() if ".staging-" in path.name or ".backup-" in path.name
    )


def test_transaction_commits_new_archive(tmp_path: Path) -> None:
    target = tmp_path / "archive"

    with ArchiveTransaction(target) as archive:
        marker = archive.reports_dir / "marker.txt"
        marker.write_text("new archive", encoding="utf-8")

        assert archive.path != target
        assert not target.exists()

    assert target.is_dir()
    assert (target / "reports" / "marker.txt").read_text(encoding="utf-8") == "new archive"
    assert _transaction_artifacts(tmp_path) == []


def test_transaction_refuses_existing_target_without_overwrite(
    tmp_path: Path,
) -> None:
    target = tmp_path / "archive"
    target.mkdir()
    marker = target / "old.txt"
    marker.write_text("old archive", encoding="utf-8")

    with (
        pytest.raises(FileExistsError, match="Archive path already exists"),
        ArchiveTransaction(target),
    ):
        pass

    assert marker.read_text(encoding="utf-8") == "old archive"
    assert _transaction_artifacts(tmp_path) == []


def test_transaction_replaces_existing_archive_after_success(
    tmp_path: Path,
) -> None:
    target = tmp_path / "archive"
    target.mkdir()
    old_marker = target / "old.txt"
    old_marker.write_text("old archive", encoding="utf-8")

    with ArchiveTransaction(target, overwrite=True) as archive:
        new_marker = archive.reports_dir / "new.txt"
        new_marker.write_text("new archive", encoding="utf-8")

        assert old_marker.read_text(encoding="utf-8") == "old archive"

    assert not old_marker.exists()
    assert (target / "reports" / "new.txt").read_text(encoding="utf-8") == "new archive"
    assert _transaction_artifacts(tmp_path) == []


def test_transaction_preserves_existing_archive_when_body_fails(
    tmp_path: Path,
) -> None:
    target = tmp_path / "archive"
    target.mkdir()
    old_marker = target / "old.txt"
    old_marker.write_text("old archive", encoding="utf-8")

    with (
        pytest.raises(RuntimeError, match="simulated write failure"),
        ArchiveTransaction(target, overwrite=True) as archive,
    ):
        new_marker = archive.reports_dir / "new.txt"
        new_marker.write_text("incomplete", encoding="utf-8")
        raise RuntimeError("simulated write failure")

    assert target.is_dir()
    assert old_marker.read_text(encoding="utf-8") == "old archive"
    assert not (target / "reports" / "new.txt").exists()
    assert _transaction_artifacts(tmp_path) == []


def test_transaction_removes_incomplete_new_archive_when_body_fails(
    tmp_path: Path,
) -> None:
    target = tmp_path / "archive"

    with (
        pytest.raises(RuntimeError, match="simulated write failure"),
        ArchiveTransaction(target) as archive,
    ):
        marker = archive.reports_dir / "new.txt"
        marker.write_text("incomplete", encoding="utf-8")
        raise RuntimeError("simulated write failure")

    assert not target.exists()
    assert _transaction_artifacts(tmp_path) == []


def test_transaction_replaces_existing_file_after_success(
    tmp_path: Path,
) -> None:
    target = tmp_path / "archive"
    target.write_text("old file", encoding="utf-8")

    with ArchiveTransaction(target, overwrite=True) as archive:
        marker = archive.reports_dir / "new.txt"
        marker.write_text("new archive", encoding="utf-8")

    assert target.is_dir()
    assert (target / "reports" / "new.txt").read_text(encoding="utf-8") == "new archive"
    assert _transaction_artifacts(tmp_path) == []
