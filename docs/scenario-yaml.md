# Scenario YAML Reference

ABMForge scenarios can be defined with YAML files and executed from the command line.

Scenario YAML is a versioned, strict contract. The current schema is
`abmforge.scenario.v1`. Complete scenario documents must declare this version
explicitly. Unknown root fields and unknown `run` fields are rejected rather
than ignored.

```bash
abmforge run examples/scenarios/wealth_baseline.yaml \
  --archive outputs/wealth_baseline \
  --overwrite
```

A scenario file describes:

- which model class to import,
- which parameters to pass,
- which random seed to use,
- how many steps to run,
- which external input files participate in reproducibility identity.

## Minimal scenario

```yaml
schema_version: abmforge.scenario.v1
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
| `schema_version` | yes | string | Must be `abmforge.scenario.v1` |
| `model` | yes | string | Import path of the model class |
| `run.steps` | yes | integer | Number of simulation steps |

## Optional fields

| Field | Required | Type | Description |
|---|---:|---|---|
| `name` | no | string or null | Scenario name |
| `parameters` | no | mapping/object | Model parameters |
| `run.seed` | no | integer or null | Random seed |
| `run.stop` | no | mapping/object | Safe declarative stop condition |
| `inputs` | no | mapping/object | Declared reproducibility inputs |
| `inputs.root` | no | string | Input root relative to the Scenario YAML directory; defaults to `.` when `inputs` is present |
| `inputs.artifacts` | no | list of strings | Portable file paths relative to `inputs.root` |
| `extensions` | no | mapping/object | Namespaced extension metadata |

## Field details

The YAML snippets in this section are **partial field fragments** used to explain
one field at a time. They are not complete runnable scenario documents and may
omit other required fields such as `schema_version`, `model`, or `run.steps`.

### `schema_version`

Every complete Scenario YAML document must declare exactly:

```yaml
schema_version: abmforge.scenario.v1
```

Missing versions fail closed. Unsupported versions are rejected instead of
being interpreted using the current parser. This prevents a future schema from
silently changing the meaning of an older research configuration.

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

## Declared input artifacts

Scenario Schema V1 can explicitly declare files whose bytes participate in the
execution identity:

```yaml
schema_version: abmforge.scenario.v1
model: my_package.models.MyModel

parameters:
  alpha: 0.2

run:
  seed: 42
  steps: 100

inputs:
  root: ..
  artifacts:
    - data/observations.csv
    - config/policy.json
```

The `inputs` block is optional. When it is absent, the Scenario declares no
input artifacts.

When `inputs` is present:

- `inputs.root` is optional and defaults to `.`.
- `inputs.root` is resolved relative to the directory containing the Scenario
  YAML file.
- `inputs.artifacts` is optional and defaults to an empty list.
- every artifact path is interpreted relative to `inputs.root`;
- artifact paths must be portable relative paths using forward slashes;
- absolute, drive-qualified, backslash-containing, or `..` artifact paths are
  rejected;
- duplicate artifact paths are rejected.

For example, if `configs/scenario.yaml` contains `inputs.root: ..`, the input
root is the parent directory of `configs/`.

Declared inputs are explicit and are not automatically discovered. ABMForge
does not inspect arbitrary files opened later by model code and silently add
them to the execution identity.

At execution time, the resolved files are converted to
`DeclaredInputIdentityV1`. Their portable paths and bytes contribute to
`ExecutionFingerprintV3`. If a declared input file changes, the V3 fingerprint
changes and safe recovery reruns the Scenario rather than reusing the earlier
run.

This mechanism identifies declared external inputs; it is not an immutable
snapshot of every external dependency used by a model.

## Strict field policy and extensions

Scenario Schema V1 accepts these root fields only:

- `schema_version`
- `name`
- `model`
- `parameters`
- `run`
- `inputs`
- `extensions`

The `run` mapping accepts only `seed`, `steps`, and `stop`. A misspelled or
unknown field is a validation error; ABMForge does not silently discard it.

The `inputs` mapping accepts only `root` and `artifacts`.

Framework or plugin-specific metadata belongs under the explicit `extensions`
mapping:

```yaml
extensions:
  org.example.plugin:
    mode: strict
    threshold: 0.25
```

ABMForge core preserves extension payloads but does not assign execution
semantics to arbitrary extension namespaces. Extension authors are responsible
for defining and validating their own namespaced payloads.

## Migrating legacy Scenario YAML

Legacy scenario files without a schema version are no longer accepted by the
strict V1 loader. Add the version as the first root field:

```yaml
# Legacy: rejected by the V1 loader
model: package.module.Model
run:
  steps: 100
```

becomes:

```yaml
schema_version: abmforge.scenario.v1
model: package.module.Model
run:
  steps: 100
```

Experiment YAML is a separate multi-run configuration format. Do **not** add
`abmforge.scenario.v1` to Experiment YAML merely because it also contains
`model` and `run` fields.

## Declarative stop conditions

Scenario Schema V1 supports a safe declarative stop condition under `run.stop`:

```yaml
schema_version: abmforge.scenario.v1
model: package.module.Model
run:
  steps: 1000
  stop:
    field: infected
    operator: le
    value: 0
```

The condition reads one public, single-level model attribute and compares it
with a scalar value. Supported operators are:

| Operator | Meaning |
|---|---|
| `eq` | equal |
| `ne` | not equal |
| `lt` | less than |
| `le` | less than or equal |
| `gt` | greater than |
| `ge` | greater than or equal |

`run.stop.field` must be a public model attribute name. Private names such as
`_state` and dotted traversal such as `state.infected` are rejected in V1.

`run.stop.value` must be a scalar YAML value: `null`, boolean, integer, float,
or string. Lists and mappings are rejected.

ABMForge does not use `eval()` and does not execute arbitrary Python
expressions from Scenario YAML.

The declarative condition follows the same timing contract as programmatic
`stop_when`: ABMForge evaluates it before the first step and after each
completed step. When it becomes true, the run status is `stopped` and the stop
reason is `stop_condition`.

A `Scenario` cannot define both programmatic `stop_when` and declarative
`stop_condition`.

### Recovery limitation

`execution-fingerprint-v3` does not yet encode declarative stop conditions.
For scientific safety, recovery therefore treats scenarios with a declarative
stop condition as non-reusable and reruns them rather than suppressing them
with a previously completed run. This is a fail-closed policy.

## Validation errors


### Error message contract

`Scenario.from_yaml(...)` raises `ScenarioValidationError`, a `ValueError`
subclass, when the YAML document cannot be parsed or validated.

Scenario validation errors are designed to be readable in both Python and the
CLI. They include:

- the human-readable validation problem,
- the scenario file path when available,
- the failing field path when the problem is field-specific,
- a short hint for common fixes.

Example CLI output:

```text
Scenario validation failed:
- Missing required field: run.steps (file: configs/baseline.yaml; field: run.steps). Hint: Set a non-negative integer number of simulation steps.
```

This error contract is part of the public alpha scenario workflow. The exact
wording may still improve before 1.0, but validation errors should remain
field-oriented and actionable.


ABMForge validates scenario YAML files before running the model.

Common validation errors include:

| Error | Meaning |
|---|---|
| `Scenario YAML document must be a mapping` | The YAML root is not an object |
| `Missing required field: schema_version` | A complete Scenario YAML document did not declare its schema |
| `Unsupported scenario schema version` | The declared schema is not supported by this ABMForge version |
| `Unknown scenario field` | The root contains a field outside the V1 contract |
| `Unknown run field` | `run` contains a field other than `seed`, `steps`, or `stop` |
| `Unknown inputs field` | `inputs` contains a field other than `root` or `artifacts` |
| `Field 'inputs' must be a mapping/object` | `inputs` is not an object |
| `Field 'inputs.artifacts' must be a list` | `inputs.artifacts` is not a YAML list |
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
