# {{ project_name }}

This is a minimal ABMForge study project generated from the built-in `policy`
researcher template.

The example model is a simple policy-intervention ABM on a `GridWorld`.
Residents differ in risk level. A policy assigns an intervention either randomly
or by risk priority. Treated residents may comply with the intervention, which
reduces their accumulated outcome burden.

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
  agents.py          # Resident response and outcome behavior
  model.py           # Model setup, policy assignment, scheduler, and recorders
scripts/
  run_baseline.py    # Small Python entry point
tests/
  test_smoke.py      # Minimal model smoke test
outputs/
  .gitkeep           # Output directory placeholder
```

The goal of this template is to demonstrate comparative policy experiments,
targeting rules, compliance, capacity constraints, and equity-oriented outcome
metrics.
