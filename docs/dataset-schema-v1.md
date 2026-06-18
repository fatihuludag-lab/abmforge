# Dataset Schema v1

**Status:** Draft, implemented  
**Schema version:** `abmforge.dataset.v1`  
**Applies to:** ABMForge `0.2.x` and later

ABMForge uses a dataset-first approach for simulation outputs. A model run should not only produce in-memory objects; it should produce structured, inspectable, and reusable research data.

Dataset Schema v1 defines the minimum tabular contract for ABMForge run outputs.

## Dataset tables

ABMForge Dataset v1 currently contains six tables:

| Table | Purpose |
|---|---|
| `runs` | Run-level metadata and execution status |
| `model_records` | Model-level time series records |
| `agent_records` | Agent-level variable records |
| `event_records` | Event queue and event status records |
| `lifecycle_records` | Agent and model lifecycle transition records |
| `errors` | Failed or recoverable error records |

The in-memory `Dataset` object stores these tables as lists of dictionaries. Exporters write these tables to JSON/JSONL, CSV, or archive formats.

## `runs`

Run-level metadata table.

| Field | Type | Required | Nullable | Description |
|---|---:|---:|---:|---|
| `run_id` | string | yes | no | Unique run identifier |
| `scenario` | string | no | yes | Scenario name |
| `model_name` | string | no | yes | Model class name |
| `parameters` | object | no | yes | Run parameters |
| `seed` | integer | no | yes | Random seed |
| `status` | string | no | yes | Run status |
| `started_at` | string | no | yes | Start timestamp |
| `ended_at` | string | no | yes | End timestamp |
| `python_version` | string | no | yes | Python version |
| `platform` | string | no | yes | Platform information |
| `abmforge_version` | string | no | yes | ABMForge version |
| `steps` | integer | no | yes | Number of completed steps |
| `stop_reason` | string | no | yes | Stop reason |
| `error` | string | no | yes | Error summary |
| `error_message` | string | no | yes | Error message |
| `exception_type` | string | no | yes | Exception type |

## `model_records`

Model-level time series table.

| Field | Type | Required | Nullable | Description |
|---|---:|---:|---:|---|
| `run_id` | string | yes | no | Run identifier |
| `step` | integer | yes | no | Simulation step |
| `time` | number | yes | no | Simulation time |
| `metric` | string | yes | no | Metric name |
| `value` | any | yes | no | Metric value |

Example use cases:

- total number of agents,
- mean wealth,
- infected population,
- segregation index,
- market price,
- volatility.

## `agent_records`

Agent-level variable table.

| Field | Type | Required | Nullable | Description |
|---|---:|---:|---:|---|
| `run_id` | string | yes | no | Run identifier |
| `step` | integer | yes | no | Simulation step |
| `time` | number | yes | no | Simulation time |
| `agent_id` | identifier | yes | no | Agent identifier |
| `agent_type` | string | yes | no | Agent class/type |
| `variable` | string | yes | no | Recorded variable name |
| `value` | any | yes | no | Recorded variable value |

Example use cases:

- agent wealth,
- infection state,
- location,
- opinion,
- inventory,
- trading state.

## `event_records`

Event-level table for scheduled or processed events.

| Field | Type | Required | Nullable | Description |
|---|---:|---:|---:|---|
| `run_id` | string | yes | no | Run identifier |
| `step` | integer | yes | no | Simulation step |
| `time` | number | yes | no | Simulation time |
| `event_id` | identifier | yes | no | Event identifier |
| `owner` | identifier | yes | yes | Owning agent or component |
| `tags` | array | yes | no | Event tags |
| `status` | string | yes | no | Event status |

Example use cases:

- scheduled events,
- cancelled events,
- processed events,
- event queue audit trails.

## `lifecycle_records`

Lifecycle transition table.

| Field | Type | Required | Nullable | Description |
|---|---:|---:|---:|---|
| `run_id` | string | yes | no | Run identifier |
| `step` | integer | yes | no | Simulation step |
| `time` | number | yes | no | Simulation time |
| `event` | string | yes | no | Lifecycle event name |
| `agent_id` | identifier | yes | yes | Agent identifier, when applicable |
| `details` | object | yes | no | Additional event details |

Example lifecycle events:

- agent creation,
- agent removal,
- model setup,
- model completion,
- policy intervention,
- state transition.

## `errors`

Error and failure table.

| Field | Type | Required | Nullable | Description |
|---|---:|---:|---:|---|
| `error_id` | string | yes | no | Error identifier |
| `run_id` | string | yes | no | Run identifier |
| `step` | integer | yes | no | Simulation step |
| `time` | number | yes | no | Simulation time |
| `component` | string | yes | yes | Component where error occurred |
| `exception_type` | string | yes | no | Exception type |
| `message` | string | yes | no | Error message |
| `traceback` | string | yes | yes | Traceback text |
| `recoverable` | boolean | yes | no | Whether the error was recoverable |
| `event_id` | identifier | yes | yes | Related event identifier |
| `agent_id` | identifier | yes | yes | Related agent identifier |
| `details` | object | yes | no | Additional details |

This table is important for experiment-native ABM because failed runs should be inspectable rather than silently discarded.

## Export formats

Current Dataset v1 export paths include:

| Method | Output |
|---|---|
| `Dataset.write_json(path)` | `runs.json` and JSONL files |
| `Dataset.write_csv(path)` | CSV files |
| `ExperimentArchive.write_run_outputs(..., format="json")` | Archive with JSON/JSONL data |
| `ExperimentArchive.write_run_outputs(..., format="parquet")` | Archive with Parquet data when data dependencies are installed |

A typical JSON archive contains:

```text
data/runs.json
data/model_records.jsonl
data/agent_records.jsonl
data/event_records.jsonl
data/lifecycle_records.jsonl
data/errors.jsonl
dataset_schema.json
manifest.json
```

## Validation

`Dataset.validate()` validates all known Dataset v1 tables against `DatasetSchemaV1`.

`Dataset.schema_errors()` returns validation errors without raising.

Validation currently checks:

- table presence,
- record object type,
- required fields,
- nullable fields,
- basic field kinds,
- known table names.

## Versioning policy

Dataset Schema v1 is the first implemented schema contract.

Compatible changes may include:

- adding optional fields,
- adding descriptions,
- adding new export formats,
- improving validation messages.

Breaking changes require a new schema version.

Examples of breaking changes:

- renaming tables,
- removing required fields,
- changing field meaning,
- changing record layout in a non-compatible way.

## Design rationale

Dataset Schema v1 is intentionally simple. It uses long-format records for model and agent variables because this makes output easier to:

- validate,
- concatenate across runs,
- query,
- export,
- archive,
- compare across parameter sweeps,
- use in reproducible research workflows.

The goal is not only to run an ABM model, but to produce research-grade simulation data.
