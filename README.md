# ABMForge

ABMForge is a lightweight, reproducible, experiment-native agent-based modeling framework for Python.

It is designed for researchers, educators, and model developers who want agent-based simulations that are easy to write, easy to reproduce, and easy to turn into analyzable datasets.

## Why ABMForge?

ABMForge focuses on three ideas:

1. **Reproducible by default**  
   Models use deterministic random number generation through model-level seeds.

2. **Experiment-native**  
   Simulations are organized around scenarios, runs, parameters, and recorded outputs.

3. **Dataset-first**  
   Model, agent, event, lifecycle, and run metadata can be exported for analysis.

ABMForge is not intended to be a clone of Mesa or NetLogo. Its long-term goal is to support reproducible computational experiments for ABM research.

## Installation

From GitHub:

```bash
git clone https://github.com/fatihuludag-lab/abmforge.git
cd abmforge
pip install -e ".[dev]"
Quick example
from abmforge import Agent, Model, Scenario
from abmforge.scheduling import RandomActivation


class Person(Agent):
    def step(self):
        self.wealth += 1


class WealthModel(Model):
    def setup(self):
        self.agents.create(Person, n=100, wealth=0)
        self.scheduler = RandomActivation(self)
        self.record.metric("total_wealth", lambda model: model.agents.sum("wealth"))

    def step(self):
        self.scheduler.step()


scenario = Scenario(model=WealthModel, seed=42, steps=10)
result = scenario.run()

print(result.dataset.model_records)
Core concepts

ABMForge currently includes:

Agent
Model
AgentCollection
GridWorld
NetworkSpace
Scheduler strategies:
SequentialActivation
RandomActivation
SimultaneousActivation
StagedActivation
Event queue
Recorder
Dataset
Scenario
Experiment
Examples

The repository includes classic ABM examples:

python examples/schelling/run.py
python examples/sir_epidemic/run.py

Current examples:

Schelling segregation model
Spatial SIR epidemic model
Wealth model
Dataset export

ABMForge can export run outputs as JSON/JSONL or CSV.

result.dataset.write_json("outputs/my_run")
result.dataset.write_csv("outputs/my_run")

Generated output folders are ignored by Git through outputs/.

Reproducibility

A typical ABMForge run records:

run ID
scenario name
model name
parameters
seed
run status
start and end timestamps
number of steps
model-level records
agent-level records
event records
lifecycle records
Development

Install development dependencies:

pip install -e ".[dev]"

Run checks:

ruff format src tests examples
ruff check src tests examples
mypy src
pytest
python -m build
Roadmap

Near-term priorities:

stronger scheduler API
more example models
parameter sweeps
reproducibility manifest
Parquet/Arrow export
event causality logs
snapshot and replay support
documentation site
Positioning

ABMForge aims to differentiate through:

reproducible scenario-based runs
dataset-first outputs
explicit event ownership
research-friendly experiment workflows
lightweight Python-first design
Contributing

Contributions are welcome. Good first areas include:

examples
documentation
tests
schedulers
spaces
export formats
reproducibility tools

Please run the full test suite before opening a pull request.

License

See LICENSE.