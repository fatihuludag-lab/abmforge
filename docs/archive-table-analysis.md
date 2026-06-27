# Archive Table Analysis

ABMForge archives are designed to be research artifacts, but researchers often
need to load archive tables into Python for custom analysis.

The `abmforge.analysis.archive_tables` helpers provide a lightweight bridge from
archive files to records or pandas DataFrames.

## Basic Usage

Load all detected archive tables:

```python
from abmforge.analysis.archive_tables import load_archive_tables

tables = load_archive_tables("outputs/baseline_archive")

runs = tables["runs"]
model_records = tables["model_records"]
```

By default, tables are returned as `list[dict]` so this API works without
additional analysis dependencies.

## Load One Table

```python
from abmforge.analysis.archive_tables import load_archive_table

model_records = load_archive_table(
    "outputs/baseline_archive",
    "model_records",
)
```

You can also pass a filename:

```python
runs = load_archive_table("outputs/baseline_archive", "runs.json")
```

## pandas DataFrames

If pandas is installed, request DataFrames:

```python
from abmforge.analysis.archive_tables import load_archive_tables

tables = load_archive_tables(
    "outputs/baseline_archive",
    as_dataframe=True,
)

model_records = tables["model_records"]
summary = model_records.groupby("metric")["value"].describe()
```

Pandas is imported lazily and remains optional.

## Explicit Table List

Load a known subset:

```python
tables = load_archive_tables(
    "outputs/baseline_archive",
    tables=["runs", "model_records"],
)
```

Ignore missing optional tables:

```python
tables = load_archive_tables(
    "outputs/baseline_archive",
    tables=["runs", "model_records", "agent_records"],
    missing="ignore",
)
```

## Supported Table Formats

The helpers recognize these files under `<archive>/data`:

- `.json`
- `.jsonl`
- `.csv`
- `.parquet`

Parquet loading requires pandas and a compatible Parquet engine.

## Standard Archive Tables

Common ABMForge archive tables include:

- `runs`
- `model_records`
- `agent_records`
- `event_records`
- `lifecycle_records`
- `errors`

Not every archive contains every table. The available tables depend on model
recording configuration and archive output format.

## Error Handling

Missing or malformed tables raise `ArchiveTableError`:

```python
from abmforge.analysis.archive_tables import ArchiveTableError, load_archive_table

try:
    errors = load_archive_table("outputs/baseline_archive", "errors")
except ArchiveTableError as exc:
    print(exc)
```

## Research Workflow

A typical analysis workflow is:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline_archive --overwrite
abmforge validate outputs/baseline_archive
python analysis/analyze.py outputs/baseline_archive
```

Inside `analysis/analyze.py`:

```python
from abmforge.analysis.archive_tables import load_archive_table

records = load_archive_table("outputs/baseline_archive", "model_records")
adoption = [
    row for row in records
    if row.get("metric") == "adoption_share"
]
```

## Limitations

This helper reads archive tables. It does not prove scientific validity, perform
calibration, or replace domain-specific analysis.

Use it as a bridge from ABMForge archives to your own analysis workflow.
