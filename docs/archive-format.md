# Experiment Archive Format

ABMForge experiment archives are directory-based research artifacts.

An archive should contain enough information to inspect, validate, summarize, and rerun a simulation experiment.

## Recommended workflow

```bash
abmforge run examples/scenarios/wealth_baseline.yaml \
  --archive outputs/wealth_baseline_archive \
  --overwrite

abmforge validate outputs/wealth_baseline_archive

abmforge summarize outputs/wealth_baseline_archive
```

## Archive layout

A typical JSON-based ABMForge archive has the following structure:

```text
archive/
  configs/
    scenario.yaml
  data/
    runs.json
    model_records.jsonl
    agent_records.jsonl
    event_records.jsonl
    lifecycle_records.jsonl
    errors.jsonl
  reports/
    run_summary.json
  logs/
  snapshots/
  manifest.json
  dataset_schema.json
```

## Top-level files

| File | Purpose |
|---|---|
| `manifest.json` | Reproducibility metadata, record counts, hashes, and environment information |
| `dataset_schema.json` | Dataset Schema v1 definition used for validation |

## `configs/`

The `configs/` directory stores configuration files used to produce the archive.

| File | Purpose |
|---|---|
| `configs/scenario.yaml` | Scenario YAML file executed by `abmforge run` |

The scenario file records:

- model import path,
- model parameters,
- random seed,
- number of steps,
- scenario name.

Without the scenario file, an archive is harder to audit and rerun.

## `data/`

The `data/` directory stores structured simulation outputs.

| File | Purpose |
|---|---|
| `runs.json` | Run-level metadata and execution status |
| `model_records.jsonl` | Model-level time series records |
| `agent_records.jsonl` | Agent-level variable records |
| `event_records.jsonl` | Event records |
| `lifecycle_records.jsonl` | Lifecycle records |
| `errors.jsonl` | Error and failure records |

These files implement Dataset Schema v1.

## `reports/`

The `reports/` directory stores derived human-readable or machine-readable reports.

| File | Purpose |
|---|---|
| `run_summary.json` | Compact summary of a single CLI run |

The CLI command below reads archive metadata and record counts:

```bash
abmforge summarize outputs/wealth_baseline_archive
```

For machine-readable output:

```bash
abmforge summarize outputs/wealth_baseline_archive --json
```

## `logs/`

The `logs/` directory is reserved for run logs.

Future versions may write:

```text
logs/run.log
logs/experiment.log
```

## `snapshots/`

The `snapshots/` directory is reserved for model snapshots and replay artifacts.

Future versions may write:

```text
snapshots/step_000100.json
snapshots/step_000100.sha256
```

## Validation

Archive validation checks the minimum archive contract.

```bash
abmforge validate outputs/wealth_baseline_archive
```

Validation checks may include:

- required directories,
- `manifest.json`,
- `dataset_schema.json`,
- non-empty `data/`,
- dataset schema hash,
- JSON/JSONL record counts,
- JSON/JSONL record hashes,
- archived scenario configuration.

A valid archive prints:

```text
Archive validation passed
```

## Reproducibility role

An ABMForge archive is designed to support reproducible research.

The archive connects:

```text
Scenario YAML
  -> Model run
  -> Dataset tables
  -> Dataset schema
  -> Manifest
  -> Validation
  -> Summary
```

For research projects, archive the following together:

- source code,
- scenario YAML files,
- generated ABMForge archives,
- analysis scripts,
- ABMForge version,
- Python version,
- dependency lock file when available.

## Compatibility note

Archive format is still evolving during the alpha phase.

Breaking changes should be avoided within Dataset Schema v1. If the archive layout changes in a non-compatible way, future versions should document a migration path.

## `run_index.json`

Current ABMForge archives write a compact `run_index.json` file at the archive root.

This file is a convenience index for experiment-level tracking. It does not replace
`data/runs.json`; instead, it duplicates selected run metadata and adds relative
archive paths that make downstream tooling easier to write.

A typical entry contains:

- `run_id`
- `scenario`
- `model_name`
- `seed`
- `status`
- `steps`
- `started_at`
- `ended_at`
- `stop_reason`
- `parameters`
- `dataset_path`
- `manifest_path`
- `dataset_schema_path`
- `summary_path`

The run index is intentionally small and JSON-based. It is useful for discovering
which runs exist in an archive before loading the full dataset tables.

Archives produced before this feature may not contain `run_index.json`.
