# {{ project_name }}

This project was generated from the ABMForge `research` template.

It is intended as a small, reproducible ABM study scaffold.

## Workflow

Run the baseline scenario:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline_archive --overwrite
abmforge validate outputs/baseline_archive
abmforge summarize outputs/baseline_archive --json
```

Run the multi-run experiment:

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment_archive --overwrite
abmforge validate outputs/experiment_archive
abmforge summarize outputs/experiment_archive --json
abmforge report outputs/experiment_archive
```

Run the lightweight analysis script:

```bash
python analysis/analyze.py outputs/experiment_archive
```

## Project Structure

```text
configs/
  baseline.yaml
  experiment.yaml
model/
  agents.py
  model.py
analysis/
  analyze.py
reports/
  README.md
outputs/
  .gitkeep
```

## Research Notes

For published work, preserve:

- the scenario or experiment configuration;
- the generated archive;
- `manifest.json`;
- `dataset_schema.json`;
- `run_index.json`;
- analysis scripts;
- source code version;
- Python environment information.

A valid ABMForge archive means the output structure is internally checkable. It
does not prove that the model is scientifically valid.
