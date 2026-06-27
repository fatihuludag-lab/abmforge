# Model Zoo Research Examples

ABMForge model zoo examples are small, executable research workflow examples.

They are not intended to be complete empirical studies. Their purpose is to
show how ABMForge models can be connected to scenario files, experiment files,
validated archives, analysis scripts, and robustness summaries.

## Current Research Examples

### Wealth Inequality

Path:

```text
examples/model_zoo/wealth_inequality/
```

Run:

```bash
cd examples/model_zoo/wealth_inequality
abmforge run configs/baseline.yaml --archive outputs/baseline_archive --overwrite
abmforge validate outputs/baseline_archive
python analysis/analyze.py outputs/baseline_archive
```

This example demonstrates:

- agent wealth state;
- stochastic transfers;
- inequality metrics;
- agent-level recording;
- archive analysis.

### Network Diffusion

Path:

```text
examples/model_zoo/network_diffusion/
```

Run:

```bash
cd examples/model_zoo/network_diffusion
abmforge run configs/baseline.yaml --archive outputs/baseline_archive --overwrite
abmforge validate outputs/baseline_archive
python analysis/analyze.py outputs/baseline_archive
```

This example demonstrates:

- network exposure;
- threshold adoption;
- parameterized diffusion;
- model-level and agent-level records;
- archive analysis.

## Recommended Workflow

For each example:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline_archive --overwrite
abmforge validate outputs/baseline_archive
abmforge summarize outputs/baseline_archive --json
python analysis/analyze.py outputs/baseline_archive
```

For experiments:

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment_archive --overwrite
abmforge validate outputs/experiment_archive
abmforge summarize outputs/experiment_archive --json
python analysis/analyze.py outputs/experiment_archive
```

## Research Caveat

A valid archive confirms that outputs satisfy ABMForge's archive expectations.
It does not prove that the model is scientifically valid or empirically
calibrated.

Researchers should still report assumptions, parameter ranges, validation
evidence, sensitivity checks, and limitations.
