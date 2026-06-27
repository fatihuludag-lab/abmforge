# Wealth Inequality Model

This example is a small economic ABM for studying how repeated stochastic
transfers can generate unequal wealth distributions.

It is intended as a research-oriented model zoo example, not as a complete
economic theory.

## Run the Baseline

From this directory:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline_archive --overwrite
abmforge validate outputs/baseline_archive
abmforge summarize outputs/baseline_archive --json
python analysis/analyze.py outputs/baseline_archive
```

## Run the Experiment

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment_archive --overwrite
abmforge validate outputs/experiment_archive
abmforge summarize outputs/experiment_archive --json
python analysis/analyze.py outputs/experiment_archive
```

## Main Outputs

The model records:

- `gini`
- `mean_wealth`
- `max_wealth`
- `total_wealth`

Agent-level `wealth` is also recorded at intervals.

## Research Use

This example can be used to demonstrate:

- inequality metrics;
- seed sensitivity;
- parameter sweeps;
- archive validation;
- archive table analysis;
- robustness summaries.

A valid archive does not imply that the model is empirically calibrated.
