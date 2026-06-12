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
