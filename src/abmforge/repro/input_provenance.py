"""Versioned provenance records for external input artifacts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

INPUT_ARTIFACT_PROVENANCE_SCHEMA_VERSION = "input-artifact-v1"
DECLARED_INPUT_IDENTITY_SCHEMA_VERSION = "declared-input-identity-v1"


@dataclass(frozen=True, slots=True)
class InputArtifactProvenanceV1:
    """Portable SHA-256 provenance for one simulation input file."""

    path: str
    size_bytes: int
    sha256: str
    role: str = "input"
    schema_version: str = INPUT_ARTIFACT_PROVENANCE_SCHEMA_VERSION

    @classmethod
    def from_path(
        cls,
        path: str | Path,
        *,
        root: str | Path | None = None,
    ) -> InputArtifactProvenanceV1:
        """Describe one input file using a portable path and SHA-256.

        When ``root`` is supplied, the resolved input must remain inside that
        root. This prevents accidental path traversal and symlink escape while
        producing a repository- or study-relative manifest path.
        """
        requested_path = Path(path)
        try:
            resolved_path = requested_path.resolve(strict=True)
        except OSError as exc:
            raise ValueError(f"Input artifact does not exist or cannot be read: {path}") from exc

        if not resolved_path.is_file():
            raise ValueError(f"Input artifact must be a file: {path}")

        if root is None:
            manifest_path = requested_path.as_posix()
        else:
            try:
                resolved_root = Path(root).resolve(strict=True)
            except OSError as exc:
                raise ValueError(f"Input artifact root does not exist: {root}") from exc

            if not resolved_root.is_dir():
                raise ValueError(f"Input artifact root must be a directory: {root}")

            try:
                manifest_path = resolved_path.relative_to(resolved_root).as_posix()
            except ValueError as exc:
                raise ValueError(f"Input artifact is outside input_root: {path}") from exc

        return cls(
            path=manifest_path,
            size_bytes=resolved_path.stat().st_size,
            sha256=_sha256_file(resolved_path),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible input provenance representation."""
        return {
            "schema_version": self.schema_version,
            "path": self.path,
            "role": self.role,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class DeclaredInputIdentityV1:
    """Canonical execution identity for explicitly declared input files."""

    artifacts: tuple[InputArtifactProvenanceV1, ...]
    artifacts_sha256: str
    schema_version: str = DECLARED_INPUT_IDENTITY_SCHEMA_VERSION

    @classmethod
    def from_paths(
        cls,
        paths: Sequence[str | Path],
        *,
        root: str | Path | None = None,
    ) -> DeclaredInputIdentityV1:
        """Describe and canonically hash one declared input set."""

        if isinstance(paths, (str, Path)):
            raise TypeError("input_artifacts must be a sequence of paths, not a scalar path")

        requested_paths = tuple(paths)

        if requested_paths and root is None:
            raise ValueError("input_root is required when input_artifacts are declared")

        artifacts = tuple(
            sorted(
                (
                    InputArtifactProvenanceV1.from_path(
                        input_path,
                        root=root,
                    )
                    for input_path in requested_paths
                ),
                key=lambda artifact: artifact.path,
            )
        )

        seen_paths: set[str] = set()
        for artifact in artifacts:
            if artifact.path in seen_paths:
                raise ValueError(f"Duplicate declared input path: {artifact.path}")
            seen_paths.add(artifact.path)

        artifacts_sha256 = cls.canonical_artifacts_sha256(
            [artifact.to_dict() for artifact in artifacts]
        )

        return cls(
            artifacts=artifacts,
            artifacts_sha256=artifacts_sha256,
        )

    @staticmethod
    def canonical_artifacts_sha256(
        records: Sequence[Mapping[str, Any]],
    ) -> str:
        """Hash input-artifact records in canonical path order."""

        canonical_records = sorted(
            (dict(record) for record in records),
            key=lambda record: str(record.get("path", "")),
        )
        return _sha256_json(canonical_records)

    @property
    def artifact_count(self) -> int:
        """Return the number of declared input artifacts."""

        return len(self.artifacts)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible declared-input identity."""

        return {
            "schema_version": self.schema_version,
            "artifact_count": self.artifact_count,
            "artifacts_sha256": self.artifacts_sha256,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256_file(
    path: Path,
    *,
    chunk_size: int = 1024 * 1024,
) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
