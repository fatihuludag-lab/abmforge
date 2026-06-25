# Getting Started

This guide gives a minimal, executable ABMForge workflow:

1. define a small model;
2. run one scenario;
3. run a small multi-seed experiment;
4. export the resulting dataset.

## Installation

For development from the repository root:

```bash
pip install -e ".[dev]"
```

Optional extras:

```bash
pip install -e ".[viz]"
pip install -e ".[analysis]"
pip install -e ".[docs]"
pip install -e ".[all]"
```

## A Minimal Executable Model

The example below is intentionally small. It is also executed in the test suite
so that the documentation stays aligned with the public API.

<!-- abmforge:execute-python -->
```python
from pathlib import Path

from abmforge import Agent, Experiment, Model, Scenario
from abmforge.scheduling import RandomActivation


class Person(Agent):
    def step(self) -> None:
        growth = self.model.parameters.get("growth", 1)
        self.wealth += growth


class WealthModel(Model):
    def setup(self) -> None:
        population = int(self.parameters.get("population", 10))
        initial_wealth = float(self.parameters.get("initial_wealth", 0.0))

        self.agents.create(Person, n=population, wealth=initial_wealth)
        self.scheduler = RandomActivation(self)
        self.record.metric("total_wealth", lambda model: model.agents.sum("wealth"))

    def step(self) -> None:
        self.scheduler.step()


scenario = Scenario(
    model=WealthModel,
    parameters={"population": 10, "initial_wealth": 0.0, "growth": 1},
    seed=42,
    steps=5,
    name="getting-started-wealth",
)

result = scenario.run()

assert result.status == "completed"
assert result.steps == 5
assert len(result.dataset.model_records) == 5

output_dir = Path("outputs/getting_started_run")
result.dataset.write_csv(output_dir)

experiment = Experiment(
    model=WealthModel,
    parameters={"population": [10], "initial_wealth": [0.0], "growth": [1, 2]},
    seeds=[1, 2],
    steps=3,
    name="getting-started-experiment",
)

experiment_result = experiment.run()

assert experiment_result.run_count == 4
assert experiment_result.failed_count == 0

experiment_output = Path("outputs/getting_started_experiment")
experiment_result.write_csv(experiment_output)

print(experiment_result.summary())
```

## Running Bundled Examples

From the repository root:

```bash
python examples/wealth_model/run.py
python examples/schelling/run.py
python examples/sir_epidemic/run.py
python examples/sugarscape/run.py
python examples/parameter_sweep/run.py
python examples/gis_space/run.py
```

## Local Checks

Before opening a pull request:

```bash
python -m ruff format src tests examples
python -m ruff check src tests examples
python -m mypy src
python -m pytest -q
python -m mkdocs build --strict
python -m build
```
