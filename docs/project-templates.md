# Project templates

ABMForge project templates provide a researcher-friendly starting point for
new studies. They create a small project structure with configuration files,
model code, tests, and an output directory.

List available templates with:

```bash
abmforge templates
```

Machine-readable output is also available:

```bash
abmforge templates --json
```

Create a new study project with:

```bash
abmforge new my-study --template grid
```

## Built-in templates

### `grid`

The `grid` template is a minimal grid-based ABM study. It includes:

```text
README.md
pyproject.toml
configs/
  baseline.yaml
  experiment.yaml
model/
  __init__.py
  agents.py
  model.py
scripts/
  run_baseline.py
tests/
  test_smoke.py
outputs/
  .gitkeep
```

The generated baseline can be run with:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
```

The generated experiment can be run with:

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
abmforge report outputs/experiment
```

## Current scope

The first template layer intentionally includes only one template. Future
templates may include network, epidemic, segregation, policy, and resource
competition starting points.
