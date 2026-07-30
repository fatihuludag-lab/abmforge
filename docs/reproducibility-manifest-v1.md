# Reproducibility Manifest V1

ABMForge's reproducibility manifest is a machine-readable JSON document that records how a model run or dataset was produced.

## Why manifests matter

A useful ABM run archive should record:

- ABMForge version
- scenario and model name
- parameters and parameter hashes
- run status
- named RNG stream policy
- record counts
- record hashes
- Python and platform metadata
- optional Git metadata
- optional package metadata
- generated artifacts

## Basic usage

```python
from abmforge import ReproducibilityManifest

manifest = ReproducibilityManifest.from_run_result(result)
manifest.write("outputs/run_42")
```

## Manifest schema

Current schema:

```text
abmforge.manifest.v1
```

Key fields:

```text
schema_version
manifest_id
created_at
abmforge_version
dataset_schema_version
dataset_schema_hash
run_id
experiment_id
status
scenario
model_name
seed
parameters_hash
record_counts
record_hashes
dataset_hash
runs
environment
git
packages
artifacts
metadata
```

## Named RNG stream policy

Generated Manifest V1 documents record the active policy identifier as
`metadata.rng_stream_policy`.

The current value is:

`named-rng-streams-v1`

This field identifies how ABMForge separates and derives named component
streams. Framework-generated manifests overwrite a conflicting user-supplied
value so the recorded policy describes the runtime contract rather than an
arbitrary annotation.

The manifest records policy identity only; it does not store generator
continuation state. Snapshots store RNG continuation state through the default
`rng_state`, the named-stream root, and opened named stream states.

Legacy manifests that predate this metadata entry may not contain
`metadata.rng_stream_policy`.

## Recommended archive layout

```text
outputs/
  run_42/
    manifest.json
    runs.json
    model_records.jsonl
    agent_records.jsonl
    event_records.jsonl
    lifecycle_records.jsonl
    errors.jsonl
```

## Future work

- event queue capture
- snapshot/restore
- deterministic replay
- failure artifacts
- ODD/TRACE export
- CoMSES packaging


## Artifact inventory and checksums

Manifest v1 can include an `artifacts` array. Each artifact records a portable
archive-relative path, file size in bytes, SHA-256 checksum, and an optional
role such as `input_config`, `dataset_table`, `dataset_schema`, `run_index`, or
`report`.

Example:

```json
{
  "path": "configs/scenario.yaml",
  "role": "input_config",
  "size_bytes": 128,
  "sha256": "..."
}
```

Archive validation checks these artifact records when they are present. This
means that changes to archived configuration files, dataset tables, schema
files, or other registered artifacts can be detected after the archive is
written.

Archive writers finalize the artifact inventory after all initial run,
experiment, CSV compatibility, and report outputs have been written. Generated
files such as `run_summary.json`, `experiment_summary.json`, and
`README_RESULTS.md` are therefore included in the checksum inventory.

When `abmforge report` adds derived reports to an existing archive, ABMForge
updates only the generated report entries. Existing artifact records and
checksums are preserved rather than re-hashing unrelated files. This prevents
report generation from silently accepting a previously modified dataset file
as trusted archive content.

Archives created before artifact inventories existed remain valid as legacy
alpha archives; artifact checksum validation only runs when `artifacts` is
present in `manifest.json`.
