# Experiment Archive Specification v1

**Status:** Draft  
**Applies to:** ABMForge alpha releases before the first beta  
**Purpose:** Define the minimum directory, metadata, dataset, validation, and compatibility contract for ABMForge experiment archives.

## 1. Scope

An ABMForge experiment archive is a directory-based research artifact.

It is intended to make simulation outputs:

- inspectable;
- validated;
- summarizable;
- queryable;
- citable;
- easier to rerun or audit.

This specification covers the archive structure and metadata contract. It does not yet guarantee full independent reconstruction of a run without preserving source code, inputs, and the execution environment.

## 2. Design Goals

A valid ABMForge archive should:

1. preserve the scenario or experiment configuration;
2. preserve run-level metadata;
3. preserve structured simulation records;
4. preserve the dataset schema;
5. preserve reproducibility metadata;
6. preserve failure information;
7. support validation;
8. support summarization and reporting;
9. allow future migration;
10. remain human-inspectable.

## 3. Archive Layout

A v1 archive should use the following logical layout:

```text
archive/
├── manifest.json
├── dataset_schema.json
├── registry.json
├── run_index.json
├── configs/
│   ├── scenario.yaml
│   └── experiment.yaml
├── data/
│   ├── runs.json
│   ├── model_records.jsonl
│   ├── agent_records.jsonl
│   ├── event_records.jsonl
│   ├── lifecycle_records.jsonl
│   └── errors.jsonl
├── reports/
│   └── run_summary.json
├── logs/
├── snapshots/
└── artifacts/
```

Implementations may omit files that do not apply to a particular archive type, but the absence of optional files must not break validation.

## 4. Required Top-Level Files

### `manifest.json`

Required.

The manifest records reproducibility and integrity metadata.

At minimum, it should include:

- archive format version;
- ABMForge version;
- Python version;
- platform information;
- creation timestamp;
- storage format;
- dataset table counts;
- dataset table hashes where available;
- scenario or experiment configuration hash where available.

### `dataset_schema.json`

Required.

The dataset schema records the Dataset Schema version used by the archive.

It should define the expected structure of the standard tables:

- `runs`;
- `model_records`;
- `agent_records`;
- `event_records`;
- `lifecycle_records`;
- `errors`.

### `run_index.json`

Required for new v1 archives.

Older alpha archives may omit it, but new archive writers should create it.

The run index is a compact discovery layer for archived runs. It should not replace `data/runs.json`; instead, it provides fast access to run identifiers, parameters, seeds, statuses, and output locations.

### `registry.json`

Optional in early alpha archives.

When present, the registry may describe archive components, storage backends, table locations, report files, and artifact references.

## 5. `configs/`

The `configs/` directory stores the user-facing configuration files that produced the archive.

Expected files:

- `configs/scenario.yaml` for single-scenario runs;
- `configs/experiment.yaml` for multi-run experiments.

At least one configuration file should be preserved when the archive was created through the CLI.

## 6. `data/`

The `data/` directory stores machine-readable simulation outputs.

Standard JSON/JSONL files:

| File | Table | Purpose |
|---|---|---|
| `runs.json` | `runs` | Run-level metadata, parameters, seed, status, timing, and stop reason |
| `model_records.jsonl` | `model_records` | Model-level time series observations |
| `agent_records.jsonl` | `agent_records` | Agent-level observations |
| `event_records.jsonl` | `event_records` | Event queue or event execution records |
| `lifecycle_records.jsonl` | `lifecycle_records` | Agent creation, removal, and lifecycle events |
| `errors.jsonl` | `errors` | Failure records and exception metadata |

Parquet-backed archives may use equivalent `.parquet` files. The logical table names remain the same.

## 7. `reports/`

The `reports/` directory stores derived summaries.

Reports are not the source of truth. They should be reproducible from the archive metadata and dataset tables.

Examples:

- `run_summary.json`;
- `experiment_summary.json`;
- `validation_report.json`;
- `human_report.md`.

## 8. `logs/`

The `logs/` directory is reserved for execution logs.

Logs are optional. They should not be required for dataset validation.

## 9. `snapshots/`

The `snapshots/` directory is reserved for model snapshots and replay artifacts.

Snapshot support is evolving. A v1 archive may contain snapshots, but the presence of snapshots does not imply full deterministic replay unless a replay contract explicitly says so.

## 10. `artifacts/`

The `artifacts/` directory stores additional user or analysis artifacts.

Examples:

- generated figures;
- derived tables;
- ODD documents;
- analysis notebooks;
- domain-specific outputs.

Artifact files should be referenced from the manifest or registry when they are part of the declared research artifact.

## 11. Run Status Semantics

A run should have one of the following statuses:

- `completed`;
- `failed`;
- `stopped`;
- `running`;
- `unknown`.

New archive writers should avoid leaving a run permanently marked as `running` after a process exits. If an archive is resumed or repaired, unfinished runs should be represented explicitly.

## 12. Failure Records

Failures are first-class research data.

A failed run should preserve:

- run identifier;
- scenario or experiment name;
- seed;
- parameters;
- exception type where safe;
- error message where safe;
- step or time where failure occurred if available.

Failure records should be present even when the experiment is configured to continue after errors.

## 13. Validation Requirements

Archive validation should check at least:

1. required directories exist;
2. `manifest.json` exists;
3. `dataset_schema.json` exists;
4. `data/` exists and is non-empty;
5. required logical tables can be read;
6. record counts match manifest metadata where available;
7. hashes match manifest metadata where available;
8. scenario or experiment configuration exists when expected;
9. run index is well formed for new v1 archives;
10. failure records are readable.

Validation should fail loudly on corrupted or unreadable core files.

## 14. Compatibility Rules

During alpha development, archive format changes may occur.

However:

- Dataset Schema v1 changes should avoid silent breaking changes;
- breaking changes should be documented;
- migration paths should be provided for non-compatible archive changes;
- readers should detect unsupported archive versions clearly.

## 15. Non-Goals for v1

A v1 archive does not, by itself, guarantee:

- full source-code preservation;
- full input-data preservation;
- environment reconstruction;
- Docker or Conda environment recreation;
- bitwise identical results across platforms;
- complete deterministic replay.

Those guarantees require additional reproducibility tiers and artifacts.

## 16. Recommended CLI Contract

A user should be able to run:

```bash
abmforge validate outputs/archive
abmforge summarize outputs/archive
abmforge report outputs/archive
```

against both single-run and multi-run archives.

## 17. Future Extensions

Future archive versions may add:

- `archive_schema.json`;
- manifest JSON Schema validation;
- source bundle references;
- input artifact hashes;
- lockfile or SBOM references;
- streaming Parquet metadata;
- deterministic replay metadata;
- migration metadata;
- signed checksums.
