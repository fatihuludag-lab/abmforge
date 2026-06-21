from __future__ import annotations

import pytest

from abmforge.experiment.archive import ExperimentArchive


def test_archive_create_refuses_existing_directory_without_overwrite(tmp_path) -> None:
    archive_path = tmp_path / "archive"
    archive_path.mkdir()
    stale_file = archive_path / "stale.txt"
    stale_file.write_text("old output", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Archive path already exists"):
        ExperimentArchive.create(archive_path)

    assert stale_file.read_text(encoding="utf-8") == "old output"


def test_archive_create_refuses_existing_file_without_overwrite(tmp_path) -> None:
    archive_path = tmp_path / "archive"
    archive_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Archive path already exists"):
        ExperimentArchive.create(archive_path)

    assert archive_path.is_file()
    assert archive_path.read_text(encoding="utf-8") == "not a directory"


def test_archive_create_overwrite_replaces_existing_directory(tmp_path) -> None:
    archive_path = tmp_path / "archive"
    archive_path.mkdir()
    stale_file = archive_path / "stale.txt"
    stale_file.write_text("old output", encoding="utf-8")

    archive = ExperimentArchive.create(archive_path, overwrite=True)

    assert archive.path == archive_path
    assert archive.path.is_dir()
    assert not stale_file.exists()
    assert archive.data_dir.is_dir()
    assert archive.snapshots_dir.is_dir()
    assert archive.reports_dir.is_dir()
    assert archive.logs_dir.is_dir()
    assert archive.configs_dir.is_dir()


def test_archive_create_overwrite_replaces_existing_file(tmp_path) -> None:
    archive_path = tmp_path / "archive"
    archive_path.write_text("not a directory", encoding="utf-8")

    archive = ExperimentArchive.create(archive_path, overwrite=True)

    assert archive.path == archive_path
    assert archive.path.is_dir()
    assert archive.data_dir.is_dir()
    assert archive.snapshots_dir.is_dir()
    assert archive.reports_dir.is_dir()
    assert archive.logs_dir.is_dir()
    assert archive.configs_dir.is_dir()
