# Reproducible Threshold-Adoption Study

This example demonstrates the intended ABMForge research workflow:

```text
model
  → experiment YAML
  → multi-run experiment archive
  → validation
  → summary
  → report
  → lightweight analysis artifacts
```

The model is intentionally compact. It is designed to show how a stochastic ABM
study can produce a traceable archive rather than only an ad hoc CSV file.

## Model

The example implements a simple threshold-adoption process.

Each consumer has:

- an `adopted` state;
- an individual adoption `threshold`;
- a sampled peer group at each step.

A non-adopter adopts when the weighted peer adoption signal plus a small
advertising term reaches the consumer's threshold.

The activation order is asynchronous and shuffled with the model-level
ABMForge random number generator. This is a deliberate modelling assumption.

## Experiment

The experiment varies:

- `peer_influence`;
- `adoption_threshold`.

It also runs multiple seeds so that stochastic variation is visible.

The primary metric is:

```text
adoption_share
```

## Reproduce

From the repository root:

```bash
python examples/reproducible_study/reproduce.py
```

Or write the archive to a custom location:

```bash
python examples/reproducible_study/reproduce.py --output C:\Temp\abmforge-study
```

The script runs:

```bash
abmforge experiment configs/experiment.yaml --archive outputs/reproducible_study_archive --overwrite
abmforge validate outputs/reproducible_study_archive
abmforge summarize outputs/reproducible_study_archive --json
abmforge report outputs/reproducible_study_archive
```

Then it writes additional analysis artifacts.

## Expected Outputs

The archive should contain:

```text
manifest.json
dataset_schema.json
run_index.json
configs/experiment.yaml
data/runs.json
data/runs.csv
data/model_records.jsonl
data/model_records.csv
reports/experiment_summary.json
reports/summary.md
reports/reproducible_study_summary.csv
reports/reproducible_study_adoption_curve.csv
reports/reproducible_study_adoption_curve.svg
```

## Why This Example Matters

This example is not meant to be a scientific claim about real adoption dynamics.

Its purpose is to show that ABMForge can help structure a stochastic simulation
study as a reusable and inspectable research artifact.

## Reviewer-facing artifacts

The `reproduce.py` script also writes a small documentation bundle into the
archive `reports/` directory:

- `ODD.md` and `ODD.json` document the model using ABMForge's ODD helper.
- `research_protocol.md` states the workflow purpose, experimental design,
  primary metric, reproducibility contract, and limitations.
- `artifact_manifest.json` records whether the expected reviewer-facing
  artifacts exist in the archive.

These files are intended to make the example easier to inspect during software
review, teaching, and reproducibility demonstrations.
