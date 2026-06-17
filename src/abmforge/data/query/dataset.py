from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

_PARQUET_TABLES = {
    "runs": "runs.parquet",
    "model_records": "model_records.parquet",
    "agent_records": "agent_records.parquet",
    "event_records": "event_records.parquet",
    "lifecycle_records": "lifecycle_records.parquet",
    "errors": "errors.parquet",
}


@dataclass(slots=True)
class ExperimentDataset:
    """Queryable interface for ABMForge experiment data archives."""

    data_dir: Path

    @classmethod
    def open(cls, path: str | Path) -> ExperimentDataset:
        """Open an ABMForge experiment data directory.

        The path may point either to the archive root or directly to its data directory.
        """
        candidate = Path(path)

        if (candidate / "data").is_dir():
            candidate = candidate / "data"

        if not candidate.is_dir():
            raise FileNotFoundError(f"Experiment data directory not found: {candidate}")

        return cls(data_dir=candidate)

    def available_tables(self) -> list[str]:
        """Return queryable Parquet tables available in the data directory."""
        return [
            table
            for table, filename in _PARQUET_TABLES.items()
            if (self.data_dir / filename).is_file()
        ]

    def require_tables(self, tables: list[str] | None = None) -> None:
        """Raise FileNotFoundError if required Parquet tables are missing."""
        required = tables or list(_PARQUET_TABLES)
        missing = [
            table
            for table in required
            if table not in _PARQUET_TABLES
            or not (self.data_dir / _PARQUET_TABLES[table]).is_file()
        ]

        if missing:
            raise FileNotFoundError("Missing queryable Parquet table(s): " + ", ".join(missing))

    def query(self, sql: str) -> Any:
        """Run a SQL query against available Parquet tables.

        Returns a pandas DataFrame.
        """
        try:
            import duckdb
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "ExperimentDataset.query requires duckdb. Install with: pip install abmforge[data]"
            ) from exc

        connection = duckdb.connect(database=":memory:")

        try:
            for table, filename in _PARQUET_TABLES.items():
                parquet_path = self.data_dir / filename

                if not parquet_path.is_file():
                    continue

                escaped_path = str(parquet_path).replace("'", "''")

                try:
                    connection.execute(
                        f"CREATE VIEW {table} AS SELECT * FROM read_parquet('{escaped_path}')"
                    )
                except Exception:
                    # DuckDB cannot read empty Parquet files with no columns.
                    # For the MVP query layer, such tables are skipped.
                    continue

            return connection.execute(sql).fetchdf()
        finally:
            connection.close()
