"""Transactional creation and replacement of experiment archives."""

from __future__ import annotations

import shutil
from pathlib import Path
from types import TracebackType
from typing import Literal
from uuid import uuid4

from abmforge.experiment.archive import ExperimentArchive


def _remove_path(path: Path) -> None:
    """Remove a file, symbolic link, or directory when it exists."""
    if not path.exists() and not path.is_symlink():
        return

    if path.is_symlink() or path.is_file():
        path.unlink()
        return

    if path.is_dir():
        shutil.rmtree(path)


class ArchiveTransaction:
    """Build an archive in staging and commit it as one replacement.

    The target archive is not modified while the transaction body is
    executing. If the body raises an exception, the staging archive is
    removed and any existing target remains unchanged.

    When the body succeeds, the staging archive replaces the target. Existing
    targets are first moved to a temporary backup so they can be restored if
    the final replacement fails.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        overwrite: bool = False,
    ) -> None:
        self.path = Path(path)
        self.overwrite = overwrite
        self._staging_path: Path | None = None
        self._archive: ExperimentArchive | None = None

    @property
    def archive(self) -> ExperimentArchive:
        """Return the staging archive while the transaction is active."""
        if self._archive is None:
            raise RuntimeError("Archive transaction has not been entered")

        return self._archive

    def __enter__(self) -> ExperimentArchive:
        """Create and return a staging archive."""
        if self.path.exists() and not self.overwrite:
            raise FileExistsError(
                f"Archive path already exists: {self.path}. Pass overwrite=True to replace it."
            )

        self.path.parent.mkdir(parents=True, exist_ok=True)

        staging_path = self.path.parent / (f".{self.path.name}.staging-{uuid4().hex}")
        self._staging_path = staging_path

        try:
            self._archive = ExperimentArchive.create(staging_path)
        except Exception:
            _remove_path(staging_path)
            self._staging_path = None
            raise

        return self._archive

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        """Rollback on body failure or commit the completed archive."""
        if exc_type is not None:
            self._rollback_staging()
            return False

        self._commit()
        return False

    def _commit(self) -> None:
        """Replace the target with the completed staging archive."""
        staging_path = self._require_staging_path()
        backup_path: Path | None = None

        try:
            if self.path.exists() or self.path.is_symlink():
                backup_path = self.path.parent / (f".{self.path.name}.backup-{uuid4().hex}")
                self.path.replace(backup_path)

            staging_path.replace(self.path)
        except Exception:
            self._recover_failed_commit(
                staging_path=staging_path,
                backup_path=backup_path,
            )
            raise
        else:
            self._staging_path = None
            self._archive = None

            if backup_path is not None:
                _remove_path(backup_path)

    def _recover_failed_commit(
        self,
        *,
        staging_path: Path,
        backup_path: Path | None,
    ) -> None:
        """Clean staging and restore the original target after commit failure."""
        rollback_error: Exception | None = None

        try:
            if self.path.exists() or self.path.is_symlink():
                _remove_path(self.path)

            if backup_path is not None and backup_path.exists():
                backup_path.replace(self.path)
        except Exception as exc:
            rollback_error = exc
        finally:
            _remove_path(staging_path)
            self._staging_path = None
            self._archive = None

        if rollback_error is not None:
            raise RuntimeError(
                "Archive commit failed and the original archive could not be restored"
            ) from rollback_error

    def _rollback_staging(self) -> None:
        """Remove an incomplete staging archive."""
        if self._staging_path is not None:
            _remove_path(self._staging_path)

        self._staging_path = None
        self._archive = None

    def _require_staging_path(self) -> Path:
        """Return the active staging path."""
        if self._staging_path is None:
            raise RuntimeError("Archive transaction has not been entered")

        return self._staging_path
