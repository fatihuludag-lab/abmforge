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
analysis_eligibility.csv
failed_runs.csv
```

## Generated files

`summary.md` is a human-readable overview of the experiment
configuration, execution statuses, analysis eligibility, final numeric
model metrics, primary-metric rankings, key findings, and execution
failures.

`metric_summary.csv` summarizes final numeric model metric values from
analysis-eligible runs. It reports run count, mean, minimum, and maximum
by metric.

A run is analysis-eligible by default when:

- its execution status is `completed` or `stopped`;
- it has at least one numeric final model metric.

`parameter_effects.csv` summarizes the configured primary metric by
parameter value using analysis-eligible runs that contain a numeric value
for that metric. It reports run count, mean, minimum, maximum, and
difference from the overall eligible-run primary-metric mean.

`primary_metric_rankings.csv` ranks full parameter combinations from
lowest to highest eligible-run mean for the configured primary metric.
Lower is not automatically better; interpret rankings according to the
scientific meaning of the metric.

`run_status.csv` counts all runs by execution status. Execution status is
reported independently from analysis eligibility.

`analysis_eligibility.csv` records the run-level analysis decision using
the following columns:

- `run_id`;
- `status`;
- `analysis_eligible`;
- `exclusion_reason`;
- `numeric_metric_count`.

Current exclusion reasons are:

- `execution_failed`;
- `execution_status_not_eligible`;
- `no_numeric_final_metrics`;
- `missing_run_id`.

`failed_runs.csv` contains execution failures only. A `stopped` run is
not classified as failed merely because execution ended before the
requested maximum number of steps.

## Execution Status and Analysis Eligibility

ABMForge treats execution status and analysis eligibility as separate
concepts.

| Execution status | Default analysis treatment |
|---|---|
| `completed` | Eligible when numeric final metrics are available |
| `stopped` | Eligible when numeric final metrics are available |
| `failed` | Excluded with `execution_failed` |
| `running`, `created`, or unknown | Excluded with `execution_status_not_eligible` |

A valid stop condition may represent a scientifically meaningful terminal
state, such as extinction, convergence, equilibrium, complete adoption,
or an epidemic ending.

Excluding every stopped run solely because of its execution status could
create status-based selection bias.

Execution status alone is not sufficient for inclusion. A completed or
stopped run with no numeric final model metric remains visible in the
archive but is excluded from default metric analysis with the reason
`no_numeric_final_metrics`.
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
