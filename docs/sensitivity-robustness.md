# Sensitivity and Robustness Summaries

ABM studies should usually report whether results are robust across seeds and
important parameter choices.

ABMForge provides lightweight helpers for summarizing metrics from archive
tables. These helpers are intentionally small and dependency-free by default.

## Why Robustness Matters

A single simulation run is rarely enough for a research claim.

Researchers should usually inspect:

- variation across random seeds;
- variation across key parameters;
- final metric distributions;
- minimum and maximum outcomes;
- whether qualitative conclusions survive plausible parameter changes.

## Basic Metric Summary

Load model records from an archive and summarize a final metric:

```python
from abmforge.analysis import load_archive_table
from abmforge.analysis.robustness import summarize_metric

model_records = load_archive_table(
    "outputs/experiment_archive",
    "model_records",
)

summary = summarize_metric(
    model_records,
    metric="adoption_share",
)

print(summary)
```

The returned summary includes:

- `metric`
- `count`
- `mean`
- `std`
- `min`
- `max`

By default, only the latest value per run is used.

## Group by Parameters

For multi-run experiments, summarize a metric by parameter values:

```python
from abmforge.analysis.robustness import summarize_metric_by_parameters

rows = summarize_metric_by_parameters(
    "outputs/experiment_archive",
    metric="adoption_share",
    group_by=["peer_influence"],
)

for row in rows:
    print(row)
```

This reads:

- `data/runs.*`
- `data/model_records.*`

and joins records by `run_id`.

## Write a CSV Summary

```python
from abmforge.analysis.robustness import (
    summarize_metric_by_parameters,
    write_summary_csv,
)

rows = summarize_metric_by_parameters(
    "outputs/experiment_archive",
    metric="adoption_share",
    group_by=["peer_influence"],
)

write_summary_csv(rows, "reports/robustness_summary.csv")
```

## Multiple Grouping Fields

```python
rows = summarize_metric_by_parameters(
    "outputs/experiment_archive",
    metric="adoption_share",
    group_by=["peer_influence", "base_threshold"],
)
```

## Latest Per Run

ABMForge model records may include time-series values. For final outcome
summaries, the default behavior is:

```python
latest_per_run=True
```

This selects the latest recorded value for each run before computing statistics.

To summarize every recorded value:

```python
summary = summarize_metric(
    model_records,
    metric="adoption_share",
    latest_per_run=False,
)
```

## Interpretation

These summaries are descriptive. They do not replace:

- calibration;
- validation against observed data;
- model checking;
- sensitivity analysis design;
- domain-specific interpretation.

A robustness summary can show that results are stable across simulated seeds or
parameters, but it does not prove the model is scientifically valid.

## Recommended Reporting

For published research, report:

- parameter ranges;
- seed policy;
- number of runs;
- final metric mean;
- standard deviation;
- minimum and maximum values;
- archive path or DOI;
- ABMForge version;
- whether the metric is final-step or time-aggregated.

## Related Tools

For richer sensitivity analysis, use the SALib-related helpers where
appropriate. The robustness helpers here are intended as a simple first layer
for archive-based reporting.
