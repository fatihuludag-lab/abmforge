from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ExperimentRegistry:
    """Registry for experiment archive runs, snapshots, and validation reports."""

    experiment_id: str
    runs: list[dict[str, Any]] = field(default_factory=list)
    snapshots: list[dict[str, Any]] = field(default_factory=list)
    validations: list[dict[str, Any]] = field(default_factory=list)

    def add_run(self, **metadata: Any) -> None:
        self.runs.append(
            {
                "registered_at": _now(),
                **metadata,
            }
        )

    def add_snapshot(self, **metadata: Any) -> None:
        self.snapshots.append(
            {
                "registered_at": _now(),
                **metadata,
            }
        )

    def add_validation(self, **metadata: Any) -> None:
        self.validations.append(
            {
                "registered_at": _now(),
                **metadata,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "runs": list(self.runs),
            "snapshots": list(self.snapshots),
            "validations": list(self.validations),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExperimentRegistry:
        experiment_id = data.get("experiment_id")
        if not isinstance(experiment_id, str):
            raise ValueError("Registry must define a string 'experiment_id'")

        return cls(
            experiment_id=experiment_id,
            runs=list(data.get("runs", [])),
            snapshots=list(data.get("snapshots", [])),
            validations=list(data.get("validations", [])),
        )

    def write(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )
        return output_path

    @classmethod
    def read(cls, path: str | Path) -> ExperimentRegistry:
        input_path = Path(path)
        data = json.loads(input_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Registry file must contain a JSON object")
        return cls.from_dict(data)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
