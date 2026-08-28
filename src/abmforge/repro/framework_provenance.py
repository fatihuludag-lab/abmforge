"""Provenance identity for the running ABMForge framework."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from abmforge._version import __version__

FRAMEWORK_PROVENANCE_SCHEMA_VERSION = "framework-provenance-v1"

_FRAMEWORK_SCOPE = "abmforge-framework"
_FRAMEWORK_NAME = "abmforge"

_INSTALL_MODE_SOURCE_CHECKOUT = "source-checkout"
_INSTALL_MODE_INSTALLED_DISTRIBUTION = "installed-distribution"
_INSTALL_MODE_UNAVAILABLE = "unavailable"

_IGNORED_CACHE_SUFFIXES = {".pyc", ".pyo"}


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


def _is_runtime_package_file(path: Path, package_root: Path) -> bool:
    relative_path = path.relative_to(package_root)

    if "__pycache__" in relative_path.parts:
        return False

    if path.suffix.lower() in _IGNORED_CACHE_SUFFIXES:
        return False

    return path.is_file()


def _package_tree_sha256(package_root: Path) -> str:
    """Return a deterministic content hash for an ABMForge package tree."""

    paths = sorted(
        (path for path in package_root.rglob("*") if _is_runtime_package_file(path, package_root)),
        key=lambda path: path.relative_to(package_root).as_posix(),
    )

    digest = hashlib.sha256()

    for path in paths:
        relative_path = path.relative_to(package_root).as_posix()
        file_digest = hashlib.sha256(path.read_bytes()).digest()

        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_digest)
        digest.update(b"\0")

    return digest.hexdigest()


def _is_abmforge_source_checkout(
    package_root: Path,
    repository_root: Path,
) -> bool:
    expected_package_root = (repository_root / "src" / "abmforge").resolve()

    return package_root.resolve() == expected_package_root


@dataclass(frozen=True, slots=True)
class FrameworkProvenanceV1:
    """Versioned provenance for the running ABMForge framework."""

    version: str
    install_mode: str
    package_tree_sha256: str | None
    repository_available: bool
    commit: str | None
    branch: str | None
    dirty: bool | None
    remote: str | None
    schema_version: str = FRAMEWORK_PROVENANCE_SCHEMA_VERSION
    scope: str = _FRAMEWORK_SCOPE
    name: str = _FRAMEWORK_NAME

    @classmethod
    def from_runtime(cls) -> FrameworkProvenanceV1:
        """Collect provenance for the currently imported ABMForge package."""

        package_root = Path(__file__).resolve().parents[1]
        return cls.from_package_root(
            package_root,
            version=__version__,
        )

    @classmethod
    def from_package_root(
        cls,
        package_root: str | Path,
        *,
        version: str,
    ) -> FrameworkProvenanceV1:
        """Collect framework provenance from an ABMForge package root."""

        root = Path(package_root).resolve()

        if not root.is_dir():
            return cls.unavailable(version=version)

        try:
            package_tree_sha256 = _package_tree_sha256(root)
        except OSError:
            return cls.unavailable(version=version)

        repository_root_text = _git_output(
            ["rev-parse", "--show-toplevel"],
            root,
        )

        if repository_root_text is None:
            return cls(
                version=version,
                install_mode=_INSTALL_MODE_INSTALLED_DISTRIBUTION,
                package_tree_sha256=package_tree_sha256,
                repository_available=False,
                commit=None,
                branch=None,
                dirty=None,
                remote=None,
            )

        repository_root = Path(repository_root_text).resolve()

        if not _is_abmforge_source_checkout(root, repository_root):
            return cls(
                version=version,
                install_mode=_INSTALL_MODE_INSTALLED_DISTRIBUTION,
                package_tree_sha256=package_tree_sha256,
                repository_available=False,
                commit=None,
                branch=None,
                dirty=None,
                remote=None,
            )

        commit = _git_output(
            ["rev-parse", "HEAD"],
            repository_root,
        )

        return cls(
            version=version,
            install_mode=_INSTALL_MODE_SOURCE_CHECKOUT,
            package_tree_sha256=package_tree_sha256,
            repository_available=commit is not None,
            commit=commit,
            branch=_git_output(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                repository_root,
            ),
            dirty=_git_dirty(repository_root),
            remote=_git_output(
                ["config", "--get", "remote.origin.url"],
                repository_root,
            ),
        )

    @classmethod
    def unavailable(
        cls,
        *,
        version: str,
    ) -> FrameworkProvenanceV1:
        """Return fail-closed provenance when runtime source is unavailable."""

        return cls(
            version=version,
            install_mode=_INSTALL_MODE_UNAVAILABLE,
            package_tree_sha256=None,
            repository_available=False,
            commit=None,
            branch=None,
            dirty=None,
            remote=None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible framework provenance payload."""

        return {
            "schema_version": self.schema_version,
            "scope": self.scope,
            "name": self.name,
            "version": self.version,
            "install_mode": self.install_mode,
            "package_tree_sha256": self.package_tree_sha256,
            "repository_available": self.repository_available,
            "commit": self.commit,
            "branch": self.branch,
            "dirty": self.dirty,
            "remote": self.remote,
        }
