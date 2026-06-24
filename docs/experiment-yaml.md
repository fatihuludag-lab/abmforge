# Experiment YAML

`Scenario.from_yaml` describes one model run. Experiment YAML describes a
multi-run experiment: a model, fixed base parameters, swept parameters, seed
generation, and run length.

```yaml
name: grid-template-experiment

model: model.model.GridTemplateModel

base_parameters:
  width: 20
  height: 20
  n_agents: 120
  initial_wealth: 10

experiment:
  parameters:
    transfer_probability: [0.20, 0.35, 0.50]
  seeds:
    count: 10
    master_seed: 20260624

run:
  steps: 25

outputs:
  primary_metric: mean_wealth
```

Run it with:

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
```

## Fields

`model` must be a fully qualified import path to a subclass of
`abmforge.Model`.

`base_parameters` contains fixed parameter values. These are included in
every run.

`experiment.parameters` contains swept parameter values. Each value must be a
non-empty list.

A parameter cannot appear in both `base_parameters` and
`experiment.parameters`.

`experiment.seeds` can be either an explicit list:

```yaml
experiment:
  seeds: [100, 101, 102]
```

or a generated list:

```yaml
experiment:
  seeds:
    count: 30
    master_seed: 20260624
```

`run.steps` is the number of model steps per run.

`outputs.primary_metric` is optional metadata used by reporting tools.

## Output structure

The first experiment YAML workflow writes a lightweight multi-run output
directory:

```text
outputs/experiment/
  configs/
    experiment.yaml
  data/
    ...
  reports/
    experiment_summary.json
    README_RESULTS.md
```

This directory is intentionally simpler than the single-run
`ExperimentArchive`. Later versions may add stricter archive validation for
multi-run experiments.
