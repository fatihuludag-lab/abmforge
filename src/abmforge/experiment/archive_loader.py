from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path
from typing import Any

from abmforge.experiment.run_index import RunIndex


def load_archive_runs(path: str | Path) -> Any:
    """Load archived run metadata.

    Returns a pandas DataFrame when pandas is installed. If pandas is not
    installed, returns a list of dictionaries.

    The loader prefers ``run_index.json`` when present and falls back to
    ``data/runs.json`` for older alpha archives.
    """
    records = load_archive_run_records(path)

    try:
        pd = import_module("pandas")
    except ModuleNotFoundError:
        return records

    return pd.DataFrame(records)


def load_archive_run_records(path: str | Path) -> list[dict[str, Any]]:
    """Load archived run metadata as plain dictionaries."""
    archive_path = Path(path)

    run_index_path = archive_path / "run_index.json"
    if run_index_path.is_file():
        index = RunIndex.read(run_index_path)
        return [entry.to_dict() for entry in index.entries]

    runs_path = archive_path / "data" / "runs.json"
    if runs_path.is_file():
        data = json.loads(runs_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("data/runs.json must contain a JSON array")

        records: list[dict[str, Any]] = []
        for record_index, record in enumerate(data):
            if not isinstance(record, dict):
                raise ValueError(f"data/runs.json[{record_index}] must be a JSON object")
            records.append(dict(record))
        return records

    raise FileNotFoundError(
        "Archive does not contain run metadata. Expected run_index.json or data/runs.json."
    )
