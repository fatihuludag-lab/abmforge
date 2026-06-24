# Reporting

`abmforge report` generates a compact researcher-facing report from a
multi-run experiment output directory created by `abmforge experiment`.

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
abmforge report outputs/experiment
```

The command writes files under `outputs/experiment/reports/`:

```text
summary.md
metric_summary.csv
run_status.csv
failed_runs.csv
```

## Generated files

`summary.md` is a human-readable overview of the experiment name, model,
number of seeds, expected run count, run statuses, final model metric
summaries, and failed or non-completed runs.

`metric_summary.csv` summarizes the final numeric model metric value for
each run. It reports run count, mean, minimum, and maximum by metric.

`run_status.csv` counts runs by status.

`failed_runs.csv` lists failed or non-completed runs when available.

## Current scope

The first reporting layer is intentionally lightweight. It does not replace
statistical analysis or publication-quality visualization. It provides a
reproducible starting point for inspecting experiment outputs before deeper
analysis.
