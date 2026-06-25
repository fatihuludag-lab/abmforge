# {{ project_name }}

This is a minimal ABMForge study project generated from the built-in
`segregation` researcher template.

The example model is a Schelling-style spatial segregation model on a
`GridWorld`. Residents belong to one of two groups. Each resident evaluates the
share of similar neighbors in its local neighborhood. If the share is below a
homophily threshold, the resident relocates to a random empty cell.

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
  agents.py          # Resident behavior
  model.py           # Model setup, GridWorld, scheduler, and recorders
scripts/
  run_baseline.py    # Small Python entry point
tests/
  test_smoke.py      # Minimal model smoke test
outputs/
  .gitkeep           # Output directory placeholder
```

The goal of this template is to provide a classic spatial ABM starting point for
researchers studying segregation, local interaction, threshold behavior, and
relocation dynamics.
