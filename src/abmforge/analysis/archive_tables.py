from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import Any, Literal, TypeAlias

ArchiveRecord: TypeAlias = dict[str, Any]
ArchiveRecords: TypeAlias = list[ArchiveRecord]
ArchiveTable: TypeAlias = ArchiveRecords | Any
MissingTablePolicy: TypeAlias = Literal["raise", "ignore"]

STANDARD_ARCHIVE_TABLES: tuple[str, ...] = (
    "runs",
    "model_records",
    "agent_records",
    "event_records",
    "lifecycle_records",
    "errors",
)

_TABLE_SUFFIXES: tuple[str, ...] = (".json", ".jsonl", ".csv", ".parquet")


class ArchiveTableError(ValueError):
    """Raised when an archive table cannot be loaded."""


def list_archive_tables(archive: str | Path) -> dict[str, Path]:
    """Return detected archive data tables by logical table name.

    The function looks under ``<archive>/data`` and recognizes JSON, JSONL, CSV,
    and Parquet table files. When multiple files with the same logical table
    name exist, the first supported suffix order wins.
    """
    data_dir = _data_dir(archive)
    if not data_dir.exists():
        return {}

    tables: dict[str, Path] = {}

    for suffix in _TABLE_SUFFIXES:
        for path in sorted(data_dir.glob(f"*{suffix}")):
            tables.setdefault(path.stem, path)

    return tables


def load_archive_table(
    archive: str | Path,
    table: str,
    *,
    as_dataframe: bool = False,
) -> ArchiveTable:
    """Load one logical table from an ABMForge archive.

    Parameters
    ----------
    archive:
        Archive root directory.
    table:
        Logical table name, for example ``"runs"`` or ``"model_records"``.
        A filename such as ``"runs.json"`` is also accepted.
    as_dataframe:
        If true, return a pandas ``DataFrame``. Pandas is imported lazily and
        remains optional.

    Returns
    -------
    list[dict[str, Any]] or pandas.DataFrame
        Records by default, or a DataFrame when requested.
    """
    table_path = _find_table_path(archive, table)
    records = _read_table_records(table_path)

    if as_dataframe:
        return _to_dataframe(records)

    return records


def load_archive_tables(
    archive: str | Path,
    tables: list[str] | tuple[str, ...] | None = None,
    *,
    as_dataframe: bool = False,
    missing: MissingTablePolicy = "raise",
) -> dict[str, ArchiveTable]:
    """Load multiple archive tables.

    If ``tables`` is omitted, all detected tables under ``<archive>/data`` are
    loaded. If ``tables`` is provided, missing tables raise by default.
    """
    archive_path = Path(archive)

    if tables is None:
        detected = list_archive_tables(archive_path)
        return {
            name: load_archive_table(
                archive_path,
                path.name,
                as_dataframe=as_dataframe,
            )
            for name, path in detected.items()
        }

    loaded: dict[str, ArchiveTable] = {}

    for table in tables:
        try:
            loaded[Path(table).stem] = load_archive_table(
                archive_path,
                table,
                as_dataframe=as_dataframe,
            )
        except ArchiveTableError:
            if missing == "ignore":
                continue
            raise

    return loaded


def _data_dir(archive: str | Path) -> Path:
    return Path(archive) / "data"


def _find_table_path(archive: str | Path, table: str) -> Path:
    data_dir = _data_dir(archive)

    if not data_dir.exists():
        raise ArchiveTableError(f"Archive data directory does not exist: {data_dir}")

    table_path = Path(table)

    if table_path.suffix:
        candidate = data_dir / table_path.name
        if candidate.exists():
            return candidate
        raise ArchiveTableError(f"Archive table does not exist: {candidate}")

    for suffix in _TABLE_SUFFIXES:
        candidate = data_dir / f"{table}{suffix}"
        if candidate.exists():
            return candidate

    supported = ", ".join(_TABLE_SUFFIXES)
    raise ArchiveTableError(
        f"Archive table '{table}' was not found in {data_dir}. Supported suffixes: {supported}."
    )


def _read_table_records(path: Path) -> ArchiveRecords:
    if path.suffix == ".json":
        return _read_json_records(path)

    if path.suffix == ".jsonl":
        return _read_jsonl_records(path)

    if path.suffix == ".csv":
        return _read_csv_records(path)

    if path.suffix == ".parquet":
        dataframe = _read_parquet_dataframe(path)
        return _dataframe_to_records(dataframe)

    raise ArchiveTableError(f"Unsupported archive table suffix: {path.suffix}")


def _read_json_records(path: Path) -> ArchiveRecords:
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return [_normalize_record(item, path=path) for item in data]

    if isinstance(data, dict):
        for key in ("records", "data", "rows"):
            value = data.get(key)
            if isinstance(value, list):
                return [_normalize_record(item, path=path) for item in value]
        return [dict(data)]

    raise ArchiveTableError(f"JSON table must contain an object or list: {path}")


def _read_jsonl_records(path: Path) -> ArchiveRecords:
    records: ArchiveRecords = []

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        item = json.loads(stripped)
        if not isinstance(item, dict):
            raise ArchiveTableError(
                f"JSONL record must be an object in {path} at line {line_number}"
            )
        records.append(dict(item))

    return records


def _read_csv_records(path: Path) -> ArchiveRecords:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _read_parquet_dataframe(path: Path) -> Any:
    pd: Any = importlib.import_module("pandas")
    return pd.read_parquet(path)


def _to_dataframe(records: ArchiveRecords) -> Any:
    pd: Any = importlib.import_module("pandas")
    return pd.DataFrame.from_records(records)


def _dataframe_to_records(dataframe: Any) -> ArchiveRecords:
    records = dataframe.to_dict(orient="records")
    return [_normalize_record(item, path=None) for item in records]


def _normalize_record(item: Any, *, path: Path | None) -> ArchiveRecord:
    if isinstance(item, dict):
        return dict(item)

    location = f" in {path}" if path is not None else ""
    raise ArchiveTableError(f"Archive table record must be an object{location}")
