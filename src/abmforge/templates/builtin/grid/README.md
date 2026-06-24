# {{ project_name }}

This is a minimal ABMForge study project generated from the built-in `grid`
researcher template.

## Run the baseline scenario

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
```

## Run the local smoke test

```bash
pytest
```

## Project layout

```text
configs/
  baseline.yaml      # Single-run scenario for `abmforge run`
  experiment.yaml    # Placeholder for future `abmforge experiment` workflow
model/
  agents.py          # Agent behavior
  model.py           # Model setup, scheduler, space, and recorders
scripts/
  run_baseline.py    # Small Python entry point
tests/
  test_smoke.py      # Minimal model smoke test
outputs/
  .gitkeep           # Output directory placeholder
```

The goal of this template is to let researchers start with a clean,
reproducible ABM project structure instead of writing boilerplate from
scratch.
