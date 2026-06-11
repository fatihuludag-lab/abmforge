from __future__ import annotations

import json
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
