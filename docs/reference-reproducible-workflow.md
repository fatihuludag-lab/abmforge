# Reference Reproducible Workflow

This page describes a reference ABMForge workflow for local, reproducibility-oriented
agent-based modelling experiments.

ABMForge is alpha-stage software. The workflow below is intended to make local
experiments easier to inspect, validate, archive, and repeat. It is not yet a
guarantee of fully self-contained or machine-independent reproduction. For long-lived
research projects, preserve model source code, input data, dependency specifications,
and the execution environment alongside ABMForge archives.

## Workflow Goal

The reference workflow answers four practical questions:

1. Can the model scenario be executed from a documented configuration?
2. Are run outputs written into a structured experiment archive?
3. Can the archive be validated after execution?
4. Can the archive be summarized and inspected without rerunning the model?

The workflow uses the example scenario:

```text
examples/scenarios/wealth_baseline.yaml
```

and writes outputs to:

```text
outputs/wealth_baseline_reference
```

## 1. Prepare the Environment

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,data,viz,analysis,docs]"
python -m pip check
```

Expected result:

```text
No broken requirements found.
```

Check the installed ABMForge version:

```bash
python -c "import abmforge; print(abmforge.__version__)"
```

## 2. Run the Scenario into an Archive

Remove any previous reference output if needed:

```bash
rm -rf outputs/wealth_baseline_reference
```

Run the scenario:

```bash
abmforge run examples/scenarios/wealth_baseline.yaml \
  --archive outputs/wealth_baseline_reference \
  --overwrite
```

Expected behavior:

- the scenario is executed,
- a run archive is created,
- dataset files are written,
- metadata and reports are generated,
- and the command exits successfully.

The exact run ID and timestamps may differ between runs.

## 3. Validate the Archive

```bash
abmforge validate outputs/wealth_baseline_reference
```

Expected result:

```text
Archive validation passed
```

Validation checks the archive structure and supported dataset integrity checks.
For Parquet dataset outputs, ABMForge also checks table presence, readability,
and row counts against manifest record counts.

## 4. Summarize the Archive

```bash
abmforge summarize outputs/wealth_baseline_reference
```

A JSON summary can also be produced:

```bash
abmforge summarize outputs/wealth_baseline_reference --json
```

The summary should report the run status, step count, record counts, and archive
location.

## 5. Inspect Expected Archive Contents

A reference archive should contain directories similar to:

```text
outputs/wealth_baseline_reference/
├── configs/
├── data/
├── logs/
├── reports/
└── snapshots/
```

Common files include:

```text
manifest.json
reports/run_summary.json
data/runs.json
data/model_records.jsonl
data/agent_records.jsonl
data/event_records.jsonl
data/lifecycle_records.jsonl
data/errors.jsonl
```

Depending on the selected export format, the `data/` directory may also contain
CSV or Parquet tables.

## 6. Interpret the Dataset Tables

ABMForge datasets are organized around a small set of table concepts:

| Table | Purpose |
|---|---|
| `runs` | run-level metadata, status, parameters, seed, timing, and errors |
| `model_records` | model-level metrics over time |
| `agent_records` | agent-level observations over time |
| `event_records` | scheduled event traces |
| `lifecycle_records` | agent lifecycle transitions |
| `errors` | structured failure information |

Empty CSV tables preserve schema headers so downstream tools can still recover
the table structure even when no rows are present.

## 7. What This Workflow Does Prove

A successful run, validation, and summary show that:

- the scenario configuration is executable,
- the archive can be created cleanly,
- required archive files are present,
- supported dataset integrity checks pass,
- and the output can be summarized after execution.

This is useful for local research workflows, teaching examples, model development,
and reviewer-facing demonstrations.

## 8. What This Workflow Does Not Yet Prove

This workflow does not yet prove full independent reproduction.

In particular, it does not by itself guarantee that:

- the model source code has been permanently archived,
- all input data files have been content-addressed,
- the dependency environment can be reconstructed exactly,
- results are byte-identical across machines,
- long-running experiments can be resumed,
- or replay/checkpoint behavior is complete.

For research use, keep the following alongside the archive:

```text
source code snapshot
input data files or hashes
dependency lock file or environment export
operating system and Python version
ABMForge version or commit hash
scenario YAML file
analysis scripts
```

## 9. Recommended Reviewer Command Sequence

For a quick local review, run:

```bash
python -m pip install -e ".[dev,data,viz,analysis,docs]"
python -m pip check

abmforge run examples/scenarios/wealth_baseline.yaml \
  --archive outputs/wealth_baseline_reference \
  --overwrite

abmforge validate outputs/wealth_baseline_reference
abmforge summarize outputs/wealth_baseline_reference --json
```

Then run the project checks:

```bash
ruff format --check src tests examples
ruff check src tests examples
mypy src
pytest
mkdocs build --strict
```

If your environment uses a matrix Python version, prefer an explicit mypy target,
for example:

```bash
mypy --python-version 3.10 src
```

or:

```bash
mypy --python-version 3.11 src
```

## 10. Recommended Next Step

After completing this reference workflow, users should inspect:

- `docs/dataset-schema-v1.md`
- `docs/experiment-archive.md`
- `docs/reproducibility-manifest-v1.md`
- `docs/scenario-yaml.md`
- `docs/model-zoo.md`

Together, these pages describe the current alpha-stage research workflow more
fully.
