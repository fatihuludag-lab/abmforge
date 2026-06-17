from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

_METADATA_FIELDS = {
    "model",
    "model_name",
    "snapshot_id",
    "created_at",
    "parent_snapshot",
    "experiment_id",
    "manifest_hash",
    "snapshot_hash",
}


def write_snapshot(snapshot: dict[str, Any], path: str | Path) -> Path:
    """Write a model snapshot to a JSON file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(snapshot, indent=2, default=str),
        encoding="utf-8",
    )

    return output_path


def read_snapshot(path: str | Path) -> dict[str, Any]:
    """Read a model snapshot from a JSON file."""
    input_path = Path(path)
    data = json.loads(input_path.read_text(encoding="utf-8"))
    return cast(dict[str, Any], data)


def snapshot_hash(
    snapshot: dict[str, Any],
    *,
    include_metadata: bool = True,
) -> str:
    """Return a deterministic SHA-256 hash for a snapshot.

    When include_metadata is False, class/type/provenance metadata is ignored so
    state-equivalent snapshots can be compared across restore operations.
    """
    comparable = deepcopy(snapshot)

    if not include_metadata:
        for field in _METADATA_FIELDS:
            comparable.pop(field, None)

        agents = comparable.get("agents", [])
        if isinstance(agents, list):
            for agent in agents:
                if isinstance(agent, dict):
                    agent.pop("type", None)
                    agent.pop("agent_type", None)

    normalized = json.dumps(
        comparable,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
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
