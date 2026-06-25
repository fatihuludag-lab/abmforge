# {{ project_name }}

This is a minimal ABMForge study project generated from the built-in `resource`
researcher template.

The example model is a renewable resource competition model on a `GridWorld`.
Foragers move toward nearby high-resource cells, harvest renewable resources,
pay a metabolism cost, and accumulate wealth.

## Run the baseline scenario

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
```

## Run the multi-run experiment

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
abmforge report outputs/experiment
```

## Run the local smoke test

```bash
pytest
```

## Project layout

```text
configs/
  baseline.yaml      # Single-run scenario for `abmforge run`
  experiment.yaml    # Multi-run experiment for `abmforge experiment`
model/
  agents.py          # Forager movement and harvesting behavior
  model.py           # Model setup, GridWorld, resources, scheduler, recorders
scripts/
  run_baseline.py    # Small Python entry point
tests/
  test_smoke.py      # Minimal model smoke test
outputs/
  .gitkeep           # Output directory placeholder
```

The goal of this template is to demonstrate resource competition, spatial
search, environmental renewal, survival pressure, and inequality-oriented
outcomes.
