from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path
from typing import Any


class Dataset:
    """In-memory dataset produced by a model run."""

    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self.runs: list[dict[str, Any]] = []
        self.model_records: list[dict[str, Any]] = []
        self.agent_records: list[dict[str, Any]] = []
        self.event_records: list[dict[str, Any]] = []
        self.lifecycle_records: list[dict[str, Any]] = []

    def add_run(self, **metadata: Any) -> None:
        """Append run-level metadata."""
        self.runs.append(dict(metadata))

    def update_last_run(self, **metadata: Any) -> None:
        """Update the latest run metadata entry."""
        if not self.runs:
            self.add_run(run_id=self.run_id)
        self.runs[-1].update(metadata)

    def record_model(self, *, step: int, time: float, metric: str, value: Any) -> None:
        self.model_records.append(
            {
                "run_id": self.run_id,
                "step": step,
                "time": time,
                "metric": metric,
                "value": value,
            }
        )

    def record_agent(
        self,
        *,
        step: int,
        time: float,
        agent_id: int | str,
        agent_type: str,
        variable: str,
        value: Any,
    ) -> None:
        self.agent_records.append(
            {
                "run_id": self.run_id,
                "step": step,
                "time": time,
                "agent_id": agent_id,
                "agent_type": agent_type,
                "variable": variable,
                "value": value,
            }
        )

    def record_event(
        self,
        *,
        step: int,
        time: float,
        event_id: int | str,
        owner: int | str | None,
        tags: list[str],
        status: str,
    ) -> None:
        self.event_records.append(
            {
                "run_id": self.run_id,
                "step": step,
                "time": time,
                "event_id": event_id,
                "owner": owner,
                "tags": tags,
                "status": status,
            }
        )

    def record_lifecycle(
        self,
        *,
        step: int,
        time: float,
        event: str,
        agent_id: int | str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.lifecycle_records.append(
            {
                "run_id": self.run_id,
                "step": step,
                "time": time,
                "event": event,
                "agent_id": agent_id,
                "details": details or {},
            }
        )

    def model_frame(self) -> Any:
        """Return model records as a pandas DataFrame when pandas is installed.

        Without pandas, this method returns a list of dictionaries.
        """
        try:
            pd = import_module("pandas")
        except ModuleNotFoundError:
            return list(self.model_records)
        return pd.DataFrame(self.model_records)

    def agent_frame(self) -> Any:
        """Return agent records as a pandas DataFrame when pandas is installed."""
        try:
            pd = import_module("pandas")
        except ModuleNotFoundError:
            return list(self.agent_records)
        return pd.DataFrame(self.agent_records)

    def to_dict(self) -> dict[str, Any]:
        """Return all dataset tables as a dictionary."""
        return {
            "runs": self.runs,
            "model_records": self.model_records,
            "agent_records": self.agent_records,
            "event_records": self.event_records,
            "lifecycle_records": self.lifecycle_records,
        }

    def write_json(self, path: str | Path) -> Path:
        """Write dataset tables to a directory as JSON/JSONL files."""
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)

        (output_dir / "runs.json").write_text(
            json.dumps(self.runs, indent=2, default=str), encoding="utf-8"
        )
        self._write_jsonl(output_dir / "model_records.jsonl", self.model_records)
        self._write_jsonl(output_dir / "agent_records.jsonl", self.agent_records)
        self._write_jsonl(output_dir / "event_records.jsonl", self.event_records)
        self._write_jsonl(output_dir / "lifecycle_records.jsonl", self.lifecycle_records)
        return output_dir

    @staticmethod
    def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
        with path.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, default=str))
                f.write("\n")
