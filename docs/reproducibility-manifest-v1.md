# Reproducibility Manifest V1

ABMForge's reproducibility manifest is a machine-readable JSON document that records how a model run or dataset was produced.

## Why manifests matter

A useful ABM run archive should record:

- ABMForge version
- scenario and model name
- parameters and parameter hashes
- run status
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

- RNG state capture
- event queue capture
- snapshot/restore
- deterministic replay
- failure artifacts
- ODD/TRACE export
- CoMSES packaging
