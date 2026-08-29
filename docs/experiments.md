# Experiments

ABMForge treats experiments as first-class objects.

A typical research workflow is:

```text
Model → Scenario → Experiment → Dataset → Analysis
```

## Scenario

A `Scenario` represents one reproducible model run.

```python
from abmforge import Scenario

scenario = Scenario(
    model=MyModel,
    parameters={"alpha": 0.5},
    seed=42,
    steps=100,
)

result = scenario.run()
```

## Experiment

An `Experiment` runs multiple scenarios generated from parameter combinations and seeds.

```python
from abmforge import Experiment

experiment = Experiment(
    model=MyModel,
    parameters={
        "alpha": [0.1, 0.5, 0.9],
        "beta": [1, 2],
    },
    seeds=[1, 2, 3],
    steps=100,
)

result = experiment.run()
```

This creates:

```text
3 alpha values × 2 beta values × 3 seeds = 18 runs
```

## ParameterGrid

```python
from abmforge import ParameterGrid

grid = ParameterGrid(
    {
        "density": [0.6, 0.8],
        "homophily": [0.3, 0.5],
    }
)

for parameters in grid:
    print(parameters)
```

## ExperimentResult

```python
summary = result.summary()
```

Example:

```python
{
    "run_count": 18,
    "successful_count": 18,
    "failed_count": 0,
    "statuses": {"completed": 18},
}
```

## Failure and partial-result contract

By default, an experiment uses fail-fast execution. The first failed scenario
stops the remaining plan and raises `ExperimentExecutionError`.

```python
from abmforge import ExperimentExecutionError

try:
    result = experiment.run()
except ExperimentExecutionError as exc:
    result = exc.result
    failed_run = exc.failed_result
```

`exc.result` is a partial `ExperimentResult`. It includes earlier completed
runs and the failed run, but excludes scenarios that were not executed.

To attempt every planned scenario:

```python
experiment = Experiment(
    scenarios=scenarios,
    continue_on_error=True,
)

result = experiment.run()
```

Programmatic execution returns the complete `ExperimentResult`, including any
failed runs. Callers should inspect:

```python
result.failed_count
result.statuses()
result.failed()
```

The CLI additionally uses a non-zero exit status whenever any run failed,
whether execution stopped early or continued through the complete plan.

## Safe recovery

When an existing run index is supplied, ABMForge reuses only completed runs with
a valid `run-identity-v2` and `execution-fingerprint-v3`. Legacy, incomplete,
tampered, source-unavailable, source-changed, framework-changed, declared-input-changed, or
`stop_when`-based executions are treated as missing and run again.

See [Safe Experiment Recovery](experiment-recovery.md) for the identity fields,
matching rules, migration behavior, and current limitations.

## Export

```python
result.write_csv("outputs/experiment")
```

This writes combined files such as:

- `runs.csv`
- `model_records.csv`
- `agent_records.csv`

## When to Use Experiments

Use `Experiment` when you need:

- parameter sweeps
- repeated random seeds
- robustness checks
- sensitivity analysis
- reproducible computational experiments
