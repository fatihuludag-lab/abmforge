# Network Diffusion Model

This example is a small network-based diffusion model.

Agents adopt when peer exposure and external influence are strong enough. The
network is a deterministic ring with configurable local radius.

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

- `adoption_share`
- `adopter_count`
- `new_adoptions`
- `mean_threshold`

Agent-level `adopted` and `threshold` are recorded at intervals.

## Research Use

This example can be used to demonstrate:

- social diffusion;
- network exposure;
- parameter sweeps;
- archive validation;
- robustness summaries by `peer_influence`.
