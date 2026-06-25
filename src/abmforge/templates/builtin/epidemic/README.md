# {{ project_name }}

This is a minimal ABMForge study project generated from the built-in `epidemic`
researcher template.

The example model is a spatial SIR epidemic model on a `GridWorld`. Individuals
can be susceptible, infected, or recovered. Susceptible individuals can become
infected through nearby infected neighbors, and infected individuals recover with
a configurable probability.

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
  agents.py          # SIR agent behavior
  model.py           # Model setup, GridWorld, scheduler, and recorders
scripts/
  run_baseline.py    # Small Python entry point
tests/
  test_smoke.py      # Minimal model smoke test
outputs/
  .gitkeep           # Output directory placeholder
```

The goal of this template is to give researchers a ready-to-run epidemic ABM
starting point with baseline, experiment, and reporting workflows.
