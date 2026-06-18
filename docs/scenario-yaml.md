# Scenario YAML Reference

ABMForge scenarios can be defined with YAML files and executed from the command line.

```bash
abmforge run examples/scenarios/wealth_baseline.yaml \
  --archive outputs/wealth_baseline \
  --overwrite
```

A scenario file describes:

- which model class to import,
- which parameters to pass,
- which random seed to use,
- how many steps to run.

## Minimal scenario

```yaml
name: wealth_baseline
model: examples.wealth_model.model.WealthModel
parameters:
  n: 100
run:
  seed: 42
  steps: 10
```

## Required fields

| Field | Required | Type | Description |
|---|---:|---|---|
| `model` | yes | string | Import path of the model class |
| `run.steps` | yes | integer | Number of simulation steps |

## Optional fields

| Field | Required | Type | Description |
|---|---:|---|---|
| `name` | no | string or null | Scenario name |
| `parameters` | no | mapping/object | Model parameters |
| `run.seed` | no | integer or null | Random seed |

## Field details

### `model`

The `model` field must be a non-empty Python import path.

```yaml
model: examples.wealth_model.model.WealthModel
```

The referenced class must be importable from the current working directory or from the installed Python environment.

Invalid examples:

```yaml
model:
  path: examples.wealth_model.model.WealthModel
```

```yaml
model: null
```

### `parameters`

The `parameters` field must be a mapping/object.

```yaml
parameters:
  n: 100
  tax_rate: 0.1
```

If omitted or set to `null`, ABMForge treats it as an empty parameter dictionary.

Invalid example:

```yaml
parameters:
  - invalid
```

### `run`

The `run` field must be a mapping/object.

```yaml
run:
  seed: 42
  steps: 100
```

Invalid example:

```yaml
run:
  - invalid
```

### `run.steps`

The `run.steps` field is required.

It must be a non-negative integer.

Valid examples:

```yaml
run:
  steps: 0
```

```yaml
run:
  steps: 100
```

Invalid examples:

```yaml
run:
  steps: -1
```

```yaml
run:
  steps: invalid
```

### `run.seed`

The `run.seed` field is optional.

It must be an integer or `null`.

Valid examples:

```yaml
run:
  seed: 42
  steps: 100
```

```yaml
run:
  seed: null
  steps: 100
```

Invalid example:

```yaml
run:
  seed: invalid
  steps: 100
```

## Validation errors

ABMForge validates scenario YAML files before running the model.

Common validation errors include:

| Error | Meaning |
|---|---|
| `Scenario YAML document must be a mapping` | The YAML root is not an object |
| `Missing required field: model` | The `model` field is missing |
| `Field 'model' must be a string` | The `model` field is not a string |
| `Field 'parameters' must be a mapping/object` | `parameters` is not an object |
| `Field 'run' must be a mapping/object` | `run` is not an object |
| `Missing required field: run.steps` | `run.steps` is missing |
| `Field 'run.steps' must be an integer` | `run.steps` is not an integer |
| `Field 'run.steps' must be non-negative` | `run.steps` is negative |
| `Field 'run.seed' must be an integer or null` | `run.seed` has an invalid type |

When using the CLI, invalid scenario files produce a clean validation message:

```text
Scenario validation failed:
- Missing required field: model
```

## Recommended workflow

```bash
abmforge run examples/scenarios/wealth_baseline.yaml \
  --archive outputs/wealth_baseline \
  --overwrite

abmforge validate outputs/wealth_baseline

abmforge summarize outputs/wealth_baseline
```

This creates a reproducible ABMForge experiment archive and then validates and summarizes it.

## Research reproducibility recommendation

For research projects, keep scenario files under version control:

```text
scenarios/
  baseline.yaml
  policy_sweep.yaml
  robustness_check.yaml
```

Each scenario file should be committed together with:

- the model code,
- the ABMForge version,
- the random seeds,
- the generated archive,
- the analysis scripts.

This makes the experiment easier to audit, rerun, and cite.
