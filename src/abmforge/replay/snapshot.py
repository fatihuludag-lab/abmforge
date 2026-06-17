from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, cast


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

    When include_metadata is False, class/type metadata is ignored so that
    state-equivalent snapshots can be compared across basic restore operations.
    """
    comparable = deepcopy(snapshot)

    if not include_metadata:
        comparable.pop("model", None)
        comparable.pop("model_name", None)

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
