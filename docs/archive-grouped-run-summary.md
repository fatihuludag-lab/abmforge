# Archive grouped run summaries

ABMForge can summarize archive-level run metadata without requiring pandas or
other analysis dependencies. Grouped summaries extend that workflow by splitting
run metadata into explicit groups before applying the standard run summary.

This page describes grouped summaries only. It does not change the archive
format, existing `summarize_archive_runs()` output, or dataset table loading.

## Basic usage

```python
from abmforge.experiment import summarize_archive_runs_by

summary = summarize_archive_runs_by(
    "outputs/my_archive",
    by="scenario",
)
```

The result contains:

- the fields used for grouping,
- the number of groups,
- one standard run summary per group.

## Grouping by one field

```python
from abmforge.experiment import summarize_run_records_by

records = [
    {"scenario": "baseline", "status": "completed", "seed": 1, "steps": 5},
    {"scenario": "baseline", "status": "failed", "seed": 2, "steps": 1},
    {"scenario": "policy", "status": "completed", "seed": 3, "steps": 10},
]

summary = summarize_run_records_by(records, by="scenario")
```

This is useful for questions such as:

- how many runs were completed per scenario,
- which scenario has failed runs,
- how step counts differ across scenarios.

## Grouping by multiple fields

```python
from abmforge.experiment import summarize_archive_runs_by

summary = summarize_archive_runs_by(
    "outputs/my_archive",
    by=["scenario", "status"],
)
```

Multi-field grouping is useful for compact run dashboards, for example:

```text
scenario=baseline, status=completed
scenario=baseline, status=failed
scenario=policy, status=completed
```

## Archive method

The same grouped summary is available from `ExperimentArchive`:

```python
from abmforge.experiment import ExperimentArchive

archive = ExperimentArchive("outputs/my_archive")
summary = archive.summarize_runs_by("scenario")
```

## Scope

Grouped summaries are intentionally dependency-free. They work on run metadata
records only. They do not load model, agent, event, lifecycle, or error tables.
For detailed table-level analysis, use archive dataset loading and query tools.
