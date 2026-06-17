from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from abmforge.data.dataset import Dataset


class ParquetStorage(Dataset):
    """Parquet storage backend for ABMForge datasets.

    This backend currently records data in memory like Dataset, then writes
    all dataset tables as Parquet files when requested.
    """

    def write_parquet(self, path: str | Path) -> Path:
        """Write dataset tables to a directory as Parquet files."""
        try:
            import pandas as pd
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "ParquetStorage requires pandas and pyarrow. "
                "Install with: pip install abmforge[data]"
            ) from exc

        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)

        self._write_table(pd, output_dir / "runs.parquet", self.runs)
        self._write_table(pd, output_dir / "model_records.parquet", self.model_records)
        self._write_table(pd, output_dir / "agent_records.parquet", self.agent_records)
        self._write_table(pd, output_dir / "event_records.parquet", self.event_records)
        self._write_table(
            pd,
            output_dir / "lifecycle_records.parquet",
            self.lifecycle_records,
        )
        self._write_table(pd, output_dir / "errors.parquet", self.errors)

        return output_dir

    @staticmethod
    def _write_table(pd: Any, path: Path, records: list[dict[str, Any]]) -> None:
        normalized = [_normalize_record(record) for record in records]
        pd.DataFrame(normalized).to_parquet(path, index=False)


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Convert nested values to JSON strings for stable Parquet output."""
    normalized: dict[str, Any] = {}

    for key, value in record.items():
        if isinstance(value, dict | list):
            normalized[key] = json.dumps(value, sort_keys=True, default=str)
        else:
            normalized[key] = value

    return normalized
