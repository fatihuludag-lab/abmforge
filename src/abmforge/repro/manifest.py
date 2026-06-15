from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib.metadata import distributions
from pathlib import Path
from typing import TYPE_CHECKING, Any

from abmforge._version import __version__

if TYPE_CHECKING:
    from abmforge.data.dataset import Dataset
    from abmforge.experiment.result import RunResult


SCHEMA_VERSION = "abmforge.manifest.v1"
_DATASET_TABLES = (
    "runs",
    "model_records",
    "agent_records",
    "event_records",
    "lifecycle_records",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json_bytes(data: Any) -> bytes:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def _sha256_json(data: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(data)).hexdigest()


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


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


def _collect_git_metadata(cwd: Path) -> dict[str, Any]:
    commit = _git_output(["rev-parse", "HEAD"], cwd)
    if commit is None:
        return {"available": False}

    status = _git_output(["status", "--porcelain"], cwd)

    return {
        "available": True,
        "commit": commit,
        "branch": _git_output(["rev-parse", "--abbrev-ref", "HEAD"], cwd),
        "dirty": bool(status),
        "remote": _git_output(["config", "--get", "remote.origin.url"], cwd),
    }


def _collect_packages() -> list[dict[str, str]]:
    packages: list[dict[str, str]] = []

    for distribution in distributions():
        name = distribution.metadata["Name"]

        if name:
            packages.append(
                {
                    "name": str(name),
                    "version": distribution.version,
                }
            )

    return sorted(packages, key=lambda item: item["name"].lower())


def _collect_environment(*, include_command: bool) -> dict[str, Any]:
    environment: dict[str, Any] = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

    if include_command:
        environment["command"] = list(sys.argv)

    return environment


def _record_counts(dataset: Dataset) -> dict[str, int]:
    return {table_name: len(getattr(dataset, table_name)) for table_name in _DATASET_TABLES}


def _record_hashes(dataset: Dataset) -> dict[str, str]:
    return {
        table_name: _sha256_json(getattr(dataset, table_name)) for table_name in _DATASET_TABLES
    }


def _last_run(dataset: Dataset) -> dict[str, Any]:
    if not dataset.runs:
        return {}
    return dict(dataset.runs[-1])


def _manifest_id_for(dataset: Dataset, record_hashes: dict[str, str]) -> str:
    source = {
        "run_id": dataset.run_id,
        "runs_hash": record_hashes["runs"],
        "model_records_hash": record_hashes["model_records"],
        "agent_records_hash": record_hashes["agent_records"],
        "event_records_hash": record_hashes["event_records"],
        "lifecycle_records_hash": record_hashes["lifecycle_records"],
    }
    return f"manifest-{_sha256_json(source)[:16]}"


@dataclass(slots=True)
class ReproducibilityManifest:
    """Machine-readable reproducibility metadata for ABMForge outputs.

    The manifest captures the minimum information needed to identify how a run
    or dataset was produced. It is intentionally dependency-free and JSON-first.
    Richer archive formats such as Parquet, DuckDB, CoMSES packages, and DOI
    deposits can build on top of this schema.
    """

    schema_version: str
    manifest_id: str
    created_at: str
    abmforge_version: str
    run_id: str
    experiment_id: str | None
    status: str | None
    scenario: str | None
    model_name: str | None
    seed: Any
    parameters_hash: str | None
    record_counts: dict[str, int]
    record_hashes: dict[str, str]
    runs: list[dict[str, Any]]
    environment: dict[str, Any]
    git: dict[str, Any] | None
    packages: list[dict[str, str]] | None
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dataset(
        cls,
        dataset: Dataset,
        *,
        experiment_id: str | None = None,
        include_git: bool = True,
        include_packages: bool = True,
        include_command: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> ReproducibilityManifest:
        """Create a reproducibility manifest from a Dataset."""
        last_run = _last_run(dataset)
        record_counts = _record_counts(dataset)
        record_hashes = _record_hashes(dataset)

        parameters = last_run.get("parameters")
        parameters_hash = _sha256_json(parameters) if parameters is not None else None

        manifest = cls(
            schema_version=SCHEMA_VERSION,
            manifest_id=_manifest_id_for(dataset, record_hashes),
            created_at=_utc_now_iso(),
            abmforge_version=__version__,
            run_id=dataset.run_id,
            experiment_id=experiment_id,
            status=_optional_str(last_run.get("status")),
            scenario=_optional_str(last_run.get("scenario")),
            model_name=_optional_str(last_run.get("model_name")),
            seed=last_run.get("seed"),
            parameters_hash=parameters_hash,
            record_counts=record_counts,
            record_hashes=record_hashes,
            runs=[dict(run) for run in dataset.runs],
            environment=_collect_environment(include_command=include_command),
            git=_collect_git_metadata(Path.cwd()) if include_git else None,
            packages=_collect_packages() if include_packages else None,
            metadata=dict(metadata or {}),
        )
        manifest.validate()
        return manifest

    @classmethod
    def from_run_result(
        cls,
        result: RunResult,
        *,
        experiment_id: str | None = None,
        include_git: bool = True,
        include_packages: bool = True,
        include_command: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> ReproducibilityManifest:
        """Create a reproducibility manifest from a RunResult."""
        merged_metadata = dict(metadata or {})
        merged_metadata.update(
            {
                "run_result_status": result.status,
                "run_result_steps": result.steps,
                "run_result_stop_reason": result.stop_reason,
            }
        )

        return cls.from_dataset(
            result.dataset,
            experiment_id=experiment_id,
            include_git=include_git,
            include_packages=include_packages,
            include_command=include_command,
            metadata=merged_metadata,
        )

    def validate(self) -> None:
        """Validate the manifest's minimum structural requirements."""
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported manifest schema version: {self.schema_version}")

        if not self.manifest_id:
            raise ValueError("manifest_id must not be empty")

        if not self.run_id:
            raise ValueError("run_id must not be empty")

        if not self.abmforge_version:
            raise ValueError("abmforge_version must not be empty")

        for table_name in _DATASET_TABLES:
            if table_name not in self.record_counts:
                raise ValueError(f"Missing record count for table: {table_name}")

            if self.record_counts[table_name] < 0:
                raise ValueError(f"Negative record count for table: {table_name}")

            if table_name not in self.record_hashes:
                raise ValueError(f"Missing record hash for table: {table_name}")

    def to_dict(self) -> dict[str, Any]:
        """Return the manifest as a JSON-serializable dictionary."""
        return {
            "schema_version": self.schema_version,
            "manifest_id": self.manifest_id,
            "created_at": self.created_at,
            "abmforge_version": self.abmforge_version,
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "status": self.status,
            "scenario": self.scenario,
            "model_name": self.model_name,
            "seed": self.seed,
            "parameters_hash": self.parameters_hash,
            "record_counts": self.record_counts,
            "record_hashes": self.record_hashes,
            "runs": self.runs,
            "environment": self.environment,
            "git": self.git,
            "packages": self.packages,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
            "n_runs": self.record_counts["runs"],
            "n_model_records": self.record_counts["model_records"],
            "n_agent_records": self.record_counts["agent_records"],
            "n_event_records": self.record_counts["event_records"],
            "n_lifecycle_records": self.record_counts["lifecycle_records"],
        }

    def to_json(self) -> str:
        """Return the manifest as pretty-printed JSON."""
        return json.dumps(
            self.to_dict(),
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    def content_hash(self) -> str:
        """Return a SHA-256 hash of the manifest contents."""
        return _sha256_json(self.to_dict())

    def write(self, path: str | Path) -> Path:
        """Write the manifest to a JSON file.

        If ``path`` is a directory or has no ``.json`` suffix, the manifest is
        written to ``path / "manifest.json"``.
        """
        output_path = Path(path)

        if output_path.suffix != ".json":
            output_path.mkdir(parents=True, exist_ok=True)
            output_path = output_path / "manifest.json"
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(self.to_json(), encoding="utf-8")
        return output_path
