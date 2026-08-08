"""Source-repository provenance for reproducible ABMForge runs."""

from __future__ import annotations

import hashlib
import inspect
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from abmforge.core.model import Model

SOURCE_REPOSITORY_PROVENANCE_SCHEMA_VERSION = "source-repository-provenance-v1"


def _git_output(args: list[str], cwd: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if completed.returncode != 0:
        return None

    output = completed.stdout.strip()
    return output or None


def _git_dirty(cwd: Path) -> bool | None:
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if completed.returncode != 0:
        return None

    return bool(completed.stdout.strip())


def _sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class SourceRepositoryProvenanceV1:
    """Portable provenance for a model's defining source file and Git repository."""

    source_available: bool
    source_path: str | None
    source_sha256: str | None
    repository_available: bool
    commit: str | None
    branch: str | None
    dirty: bool | None
    remote: str | None
    schema_version: str = SOURCE_REPOSITORY_PROVENANCE_SCHEMA_VERSION

    @classmethod
    def from_model(
        cls,
        model: type[Model] | Model,
    ) -> SourceRepositoryProvenanceV1:
        """Collect provenance from a model class or instance.

        Git discovery starts from the model's defining source file, never from
        the caller's current working directory.
        """
        model_type = model if isinstance(model, type) else type(model)

        try:
            source_file = inspect.getsourcefile(model_type)
        except (OSError, TypeError):
            source_file = None

        if source_file is None:
            return cls.unavailable()

        source_path = Path(source_file).resolve()
        try:
            source_sha256 = _sha256_file(source_path)
        except OSError:
            return cls.unavailable()

        repository_root_text = _git_output(
            ["rev-parse", "--show-toplevel"],
            source_path.parent,
        )
        if repository_root_text is None:
            return cls(
                source_available=True,
                source_path=source_path.name,
                source_sha256=source_sha256,
                repository_available=False,
                commit=None,
                branch=None,
                dirty=None,
                remote=None,
            )

        repository_root = Path(repository_root_text).resolve()
        try:
            relative_source_path = source_path.relative_to(repository_root).as_posix()
        except ValueError:
            relative_source_path = source_path.name

        commit = _git_output(["rev-parse", "HEAD"], repository_root)
        dirty = _git_dirty(repository_root)

        return cls(
            source_available=True,
            source_path=relative_source_path,
            source_sha256=source_sha256,
            repository_available=commit is not None,
            commit=commit,
            branch=_git_output(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                repository_root,
            ),
            dirty=dirty,
            remote=_git_output(
                ["config", "--get", "remote.origin.url"],
                repository_root,
            ),
        )

    @classmethod
    def unavailable(cls) -> SourceRepositoryProvenanceV1:
        """Return a fail-closed provenance value for unavailable source."""
        return cls(
            source_available=False,
            source_path=None,
            source_sha256=None,
            repository_available=False,
            commit=None,
            branch=None,
            dirty=None,
            remote=None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible provenance representation."""
        return {
            "schema_version": self.schema_version,
            "scope": "model-source",
            "source_available": self.source_available,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "available": self.repository_available,
            "commit": self.commit,
            "branch": self.branch,
            "dirty": self.dirty,
            "remote": self.remote,
        }
