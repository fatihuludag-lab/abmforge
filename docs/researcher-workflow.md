# Researcher workflow

ABMForge can be used as a Python framework, but research users often need a
project workflow before they need advanced framework extension points.

The researcher workflow starts from a generated study project:

```bash
abmforge new my-study --template grid
cd my-study
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
```

The generated project separates scientific model code from configuration and
outputs:

```text
configs/
  baseline.yaml
  experiment.yaml
model/
  agents.py
  model.py
scripts/
  run_baseline.py
tests/
  test_smoke.py
outputs/
```

The initial template is intentionally small. It is designed to show the
minimum research workflow:

1. define agent behavior;
2. define model setup, scheduler, space, and recorders;
3. run a scenario YAML file;
4. write a reproducible ABMForge archive;
5. validate and summarize the output.

## List available templates

```bash
abmforge templates
```

Use JSON output when another tool needs to inspect templates:

```bash
abmforge templates --json
```

## Create a project

```bash
abmforge new demo-study --template grid
```

Existing non-empty directories are not overwritten by default. Use
`--force` only when you intentionally want to recreate the project:

```bash
abmforge new demo-study --template grid --force
```

## Run the baseline

```bash
cd demo-study
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
```

## Run a multi-run experiment

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
```

This reads the generated `configs/experiment.yaml`, expands the parameter grid,
runs each seed, writes combined CSV tables, and creates a compact experiment
summary under `outputs/experiment/reports/`.

## Generate a researcher report

```bash
abmforge report outputs/experiment
```

This creates `summary.md`, `metric_summary.csv`, `run_status.csv`, and
`failed_runs.csv` under `outputs/experiment/reports/`.

## Validate the archive

```bash
abmforge validate outputs/baseline
```

## Summarize the archive

```bash
abmforge summarize outputs/baseline
```

## Current scope

The first researcher workflow layer only adds project scaffolding. Future
layers are expected to add:

- experiment YAML execution;
- automatic report generation;
- additional built-in templates;
- optional plotting and notebook helpers.
