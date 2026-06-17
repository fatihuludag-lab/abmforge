# Experiment Archive

ABMForge experiment archives are directory-based outputs designed to make
agent-based simulation experiments reproducible, inspectable, and publishable.

A standard experiment archive has the following structure:

```text
experiment_name/
├── scenario.yaml
├── manifest.json
├── dataset_schema.json
├── data/
│   ├── runs.json
│   ├── model_records.jsonl
│   ├── agent_records.jsonl
│   ├── event_records.jsonl
│   ├── lifecycle_records.jsonl
│   └── errors.jsonl
├── snapshots/
├── reports/
└── logs/
Design goals
preserve scenario configuration
preserve run metadata
preserve dataset schema
preserve machine-readable reproducibility metadata
keep outputs easy to inspect
support future Parquet and DuckDB storage backends
support future deterministic replay
Minimum valid archive

A minimum valid archive must contain:

manifest.json
dataset_schema.json
data/
at least one dataset output file
Future extensions

Future versions may add:

Parquet tables
DuckDB database files
deterministic snapshots
replay traces
validation reports
calibration reports
ODD documentation
