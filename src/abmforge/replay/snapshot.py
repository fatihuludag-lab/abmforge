from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

_TOP_LEVEL_METADATA_FIELDS = {
    "model",
    "model_name",
    "snapshot_id",
    "created_at",
    "parent_snapshot",
    "experiment_id",
    "manifest_hash",
    "snapshot_hash",
}

_STRUCTURAL_TYPE_FIELDS = {
    "type",
    "agent_type",
}


def _is_user_state_path(path: tuple[str | int, ...]) -> bool:
    """Return whether a path belongs to user-controlled snapshot state."""
    if path and path[0] in {"parameters", "model_state"}:
        return True

    return (
        len(path) >= 3 and path[0] == "agents" and isinstance(path[1], int) and path[2] == "state"
    )


def _normalize_snapshot_value(
    value: Any,
    *,
    include_metadata: bool,
    path: tuple[str | int, ...] = (),
) -> Any:
    """Return the canonical value used for replay hashing and comparison."""
    if include_metadata:
        return deepcopy(value)

    if isinstance(value, dict):
        normalized: dict[Any, Any] = {}

        for key, item in value.items():
            if not path and key in _TOP_LEVEL_METADATA_FIELDS:
                continue

            if key in _STRUCTURAL_TYPE_FIELDS and not _is_user_state_path(path):
                continue

            normalized[key] = _normalize_snapshot_value(
                item,
                include_metadata=False,
                path=(*path, key),
            )

        return normalized

    if isinstance(value, list):
        return [
            _normalize_snapshot_value(
                item,
                include_metadata=False,
                path=(*path, index),
            )
            for index, item in enumerate(value)
        ]

    return deepcopy(value)


def write_snapshot(snapshot: dict[str, Any], path: str | Path) -> Path:
    """Write a model snapshot to a JSON file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    serialized = json.dumps(
        snapshot,
        indent=2,
        allow_nan=False,
    )
    output_path.write_text(
        serialized,
        encoding="utf-8",
    )

    return output_path


def read_snapshot(path: str | Path) -> dict[str, Any]:
    """Read a model snapshot from a JSON file."""
    input_path = Path(path)
    data = json.loads(input_path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError("Snapshot JSON must contain an object")

    return data


def snapshot_hash(
    snapshot: dict[str, Any],
    *,
    include_metadata: bool = True,
) -> str:
    """Return a deterministic SHA-256 hash for a snapshot.

    When include_metadata is False, class/type/provenance metadata is ignored so
    state-equivalent snapshots can be compared across restore operations.
    """
    comparable = _normalize_snapshot_value(
        snapshot,
        include_metadata=include_metadata,
    )

    normalized = json.dumps(
        comparable,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def attach_snapshot_hash(
    snapshot: dict[str, Any],
    *,
    include_metadata: bool = False,
) -> dict[str, Any]:
    """Return a copy of the snapshot with a deterministic snapshot hash attached."""
    snapshot_with_hash = dict(snapshot)
    snapshot_with_hash["snapshot_hash"] = snapshot_hash(
        snapshot_with_hash,
        include_metadata=include_metadata,
    )
    return snapshot_with_hash


def link_snapshot(
    parent: dict[str, Any],
    child: dict[str, Any],
) -> dict[str, Any]:
    """Return a copy of child linked to parent through snapshot lineage."""
    linked = dict(child)

    parent_snapshot_id = parent.get("snapshot_id")
    if not isinstance(parent_snapshot_id, str):
        raise ValueError("Parent snapshot must define a string 'snapshot_id'")

    linked["parent_snapshot"] = parent_snapshot_id

    return linked
