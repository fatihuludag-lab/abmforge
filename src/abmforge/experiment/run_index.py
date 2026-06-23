from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, cast

from abmforge.data.dataset import Dataset

RUN_INDEX_SCHEMA_VERSION = "run-index-v1"


@dataclass(slots=True)
class RunIndexEntry:
    """Compact index entry for one archived run."""

    run_id: str
    scenario: str | None = None
    model_name: str | None = None
    seed: int | None = None
    status: str | None = None
    steps: int | None = None
    started_at: str | None = None
    ended_at: str | None = None
    stop_reason: str | None = None
    archive_path: str = "."
    dataset_path: str = "data"
    summary_path: str | None = None
    manifest_path: str = "manifest.json"
    dataset_schema_path: str = "dataset_schema.json"
    parameters: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    error_message: str | None = None
    exception_type: str | None = None

    @classmethod
    def from_run_metadata(cls, metadata: Mapping[str, Any]) -> RunIndexEntry:
        """Create an index entry from a Dataset ``runs`` table record."""
        return cls.from_dict(metadata)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> RunIndexEntry:
        """Create an index entry from a JSON-compatible mapping."""
        return cls(
            run_id=_required_str(data, "run_id"),
            scenario=_optional_str(data.get("scenario")),
            model_name=_optional_str(data.get("model_name")),
            seed=_optional_int(data.get("seed")),
            status=_optional_str(data.get("status")),
            steps=_optional_int(data.get("steps")),
            started_at=_optional_str(data.get("started_at")),
            ended_at=_optional_str(data.get("ended_at")),
            stop_reason=_optional_str(data.get("stop_reason")),
            archive_path=_optional_str(data.get("archive_path")) or ".",
            dataset_path=_optional_str(data.get("dataset_path")) or "data",
            summary_path=_optional_str(data.get("summary_path")),
            manifest_path=_optional_str(data.get("manifest_path")) or "manifest.json",
            dataset_schema_path=_optional_str(data.get("dataset_schema_path"))
            or "dataset_schema.json",
            parameters=_parameters(data.get("parameters")),
            error=_optional_str(data.get("error")),
            error_message=_optional_str(data.get("error_message")),
            exception_type=_optional_str(data.get("exception_type")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return this entry as a JSON-compatible dictionary."""
        return asdict(self)


@dataclass(slots=True)
class RunIndex:
    """Compact experiment-level index of archived runs."""

    entries: list[RunIndexEntry] = field(default_factory=list)
    schema_version: str = RUN_INDEX_SCHEMA_VERSION

    @classmethod
    def from_dataset(cls, dataset: Dataset) -> RunIndex:
        """Build a run index from a Dataset ``runs`` table."""
        entries = [RunIndexEntry.from_run_metadata(record) for record in dataset.runs]
        return cls(entries=entries)

    @classmethod
    def read(cls, path: str | Path) -> RunIndex:
        """Read a run index from disk."""
        index_path = Path(path)

        try:
            payload = json.loads(index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid run index JSON: {exc}") from exc

        if not isinstance(payload, dict):
            raise ValueError("run_index.json must contain a JSON object")

        data = cast(dict[str, Any], payload)
        schema_version = data.get("schema_version")

        if schema_version != RUN_INDEX_SCHEMA_VERSION:
            raise ValueError(
                "Unsupported run index schema version: "
                f"{schema_version!r}; expected {RUN_INDEX_SCHEMA_VERSION!r}"
            )

        entries_data = data.get("entries")
        if not isinstance(entries_data, list):
            raise ValueError("run_index.json must contain an 'entries' array")

        entries: list[RunIndexEntry] = []
        for index, entry_data in enumerate(entries_data):
            if not isinstance(entry_data, dict):
                raise ValueError(f"run_index.json entries[{index}] must be a JSON object")
            entries.append(RunIndexEntry.from_dict(cast(dict[str, Any], entry_data)))

        return cls(entries=entries, schema_version=RUN_INDEX_SCHEMA_VERSION)

    def find(self, run_id: str) -> RunIndexEntry | None:
        """Return the entry for ``run_id`` when present."""
        for entry in self.entries:
            if entry.run_id == run_id:
                return entry
        return None

    def to_dict(self) -> dict[str, Any]:
        """Return this index as a JSON-compatible dictionary."""
        return {
            "schema_version": self.schema_version,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    def write(self, path: str | Path) -> Path:
        """Write this run index to disk."""
        index_path = Path(path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )
        return index_path


def _required_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if value is None:
        raise ValueError(f"run metadata is missing required field: {key}")
    return str(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parameters(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}
