from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from abmforge.data.dataset import Dataset
from abmforge.data.schema import DatasetSchemaV1


class ParquetStorage(Dataset):
    """Parquet storage backend for ABMForge datasets.

    This backend currently records data in memory like Dataset, then writes
    all dataset tables as Parquet files when requested.
    """

    def write_parquet(self, path: str | Path) -> Path:
        """Write dataset tables to a directory as Parquet files."""
        self.validate()

        try:
            import pandas as pd
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "ParquetStorage requires pandas and pyarrow. "
                "Install with: pip install abmforge[data]"
            ) from exc

        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)

        self._write_table(
            pd,
            output_dir / "runs.parquet",
            self.runs,
            table_name="runs",
        )
        self._write_table(
            pd,
            output_dir / "model_records.parquet",
            self.model_records,
            table_name="model_records",
        )
        self._write_table(
            pd,
            output_dir / "agent_records.parquet",
            self.agent_records,
            table_name="agent_records",
        )
        self._write_table(
            pd,
            output_dir / "event_records.parquet",
            self.event_records,
            table_name="event_records",
        )
        self._write_table(
            pd,
            output_dir / "lifecycle_records.parquet",
            self.lifecycle_records,
            table_name="lifecycle_records",
        )
        self._write_table(
            pd,
            output_dir / "errors.parquet",
            self.errors,
            table_name="errors",
        )

        return output_dir

    @staticmethod
    def _write_table(
        pd: Any,
        path: Path,
        records: list[dict[str, Any]],
        *,
        table_name: str,
    ) -> None:
        normalized = [_normalize_record(record) for record in records]

        schema_columns = [field.name for field in DatasetSchemaV1.tables[table_name].fields]

        extra_columns = sorted(
            {key for record in normalized for key in record} - set(schema_columns)
        )

        columns = [*schema_columns, *extra_columns]
        frame = pd.DataFrame(normalized, columns=columns)
        frame.to_parquet(path, index=False)


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Convert nested values to JSON strings for stable Parquet output."""
    normalized: dict[str, Any] = {}

    for key, value in record.items():
        if isinstance(value, dict | list):
            normalized[key] = json.dumps(value, sort_keys=True, default=str)
        else:
            normalized[key] = value

    return normalized
