# {{ project_name }}

This is a minimal ABMForge study project generated from the built-in `network`
researcher template.

The example model is a simple network diffusion model. Residents are placed on
network nodes. A resident adopts when enough neighboring residents have adopted,
or through a small broadcast probability.

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
  agents.py          # Network agent behavior
  model.py           # Model setup, NetworkSpace, scheduler, and recorders
scripts/
  run_baseline.py    # Small Python entry point
tests/
  test_smoke.py      # Minimal model smoke test
outputs/
  .gitkeep           # Output directory placeholder
```

The goal of this template is to show how ABMForge can support network-based
agent-based modelling workflows without requiring researchers to write project
boilerplate from scratch.
