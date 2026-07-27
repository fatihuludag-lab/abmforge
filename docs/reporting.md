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
parameter_effects.csv
primary_metric_rankings.csv
run_status.csv
failed_runs.csv
```

## Generated files

`summary.md` is a human-readable overview of the experiment name, model,
number of seeds, expected run count, run statuses, final model metric
summaries, primary-metric rankings, key findings, and failed or
non-completed runs.

`metric_summary.csv` summarizes final numeric model metric values from
runs whose status is exactly `completed`. It reports run count, mean, minimum,
and maximum by metric.

`parameter_effects.csv` summarizes the configured primary metric by parameter
value using completed runs only. It reports run count, mean, minimum, maximum,
and difference from the overall completed-run primary-metric mean.

`primary_metric_rankings.csv` ranks full parameter combinations from lowest
to highest completed-run mean for the configured primary metric. Lower is not
always better; interpret this ranking according to the scientific meaning of
the metric.

`run_status.csv` counts all runs by status.

`failed_runs.csv` lists failed or non-completed runs when available. Failed,
stopped, running, and unknown runs remain visible here but are excluded from
metric summaries, parameter effects, and primary-metric rankings.

## Manifest updates

When the target experiment directory contains `manifest.json`, `abmforge
report` adds or refreshes artifact records for the six report files it
generates.

Existing artifact entries and checksums are preserved. The reporting command
does not re-hash unrelated dataset, configuration, schema, or index files. This
ensures that report generation cannot silently accept earlier modifications to
the research archive.

Report generation also remains compatible with legacy or plain experiment
directories that do not contain a manifest. In that case, the reports are
written without creating a new `manifest.json`.

## Current scope

The reporting layer is intentionally lightweight. It does not replace
statistical analysis or publication-quality visualization. It provides a
reproducible starting point for inspecting experiment outputs before deeper
analysis.
