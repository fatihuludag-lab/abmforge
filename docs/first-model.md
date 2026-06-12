# First Model

This page shows how to build a minimal ABMForge model.

## Basic Structure

An ABMForge model usually has two classes:

- an `Agent` subclass
- a `Model` subclass

The agent defines individual behavior. The model defines setup, scheduling, recording, and simulation logic.

## Example

```python
from abmforge import Agent, Model, Scenario
from abmforge.scheduling import RandomActivation


class Person(Agent):
    def step(self) -> None:
        self.wealth += 1


class WealthModel(Model):
    def setup(self) -> None:
        self.agents.create(Person, n=100, wealth=0)
        self.scheduler = RandomActivation(self)

        self.record.metric(
            "total_wealth",
            lambda model: model.agents.sum("wealth"),
        )

    def step(self) -> None:
        self.scheduler.step()


scenario = Scenario(
    model=WealthModel,
    seed=42,
    steps=10,
)

result = scenario.run()

print(result.dataset.model_records)
```

## What Happens?

1. `Person` defines agent-level behavior.
2. `WealthModel.setup()` creates agents.
3. `RandomActivation` activates agents in random order.
4. `record.metric()` records model-level data.
5. `Scenario` runs the model reproducibly.
6. `result.dataset` stores output records.

## Agent

Agents are Python objects with access to:

- `self.model`
- `self.unique_id`
- `self.rng`

## Model

Models define:

- parameters
- random generator
- agents
- event queue
- recorder
- world or space

## Scenario

A scenario describes one reproducible model run.

## Dataset

The dataset stores:

- run metadata
- model-level records
- agent-level records
- event records
- lifecycle records
