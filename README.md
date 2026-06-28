# ABMForge

ABMForge is a lightweight, Python-first alpha framework for agent-based modeling, with first-class support for scenarios, structured datasets, and reproducibility-oriented metadata.

It is designed for researchers, educators, model developers, and Python users who want to build agent-based simulations that are easy to write, easier to inspect, easier to analyze, and easier to reproduce when source code, inputs, and environments are preserved.

## Why ABMForge?

ABMForge focuses on four principles:

1. **Reproducibility-oriented**
   Model runs can be controlled with deterministic seeds and reproducibility metadata, while full reconstruction still depends on preserving source code, inputs, and environments.

2. **Experiment-native**  
   Simulations are organized around scenarios, parameter grids, multi-seed experiments, and run results.

3. **Dataset-first**  
   Model-level, agent-level, event-level, lifecycle, and run metadata can be recorded and exported.

4. **Python-first and lightweight**  
   The core is intentionally small, typed, and easy to inspect.

ABMForge is not intended to be a clone of Mesa, NetLogo, or AgentPy. Its goal is to provide a research-friendly ABM workflow centered on reproducibility, experiments, datasets, and extensibility.

## Positioning

ABMForge is designed around a research workflow:

Model → Scenario → Experiment → Dataset → Analysis → Visualization

The framework emphasizes:

- reproducibility
- experiment management
- dataset-oriented outputs
- lightweight architecture
- extensibility

Rather than focusing only on simulation execution, ABMForge aims to support the complete lifecycle of computational experiments.

## Key Features

ABMForge currently provides:

### Core Modeling

- Agent
- Model
- AgentCollection

### Spaces

- GridWorld
- NetworkSpace
- ContinuousSpace
- GISSpace

### Scheduling

- SequentialActivation
- RandomActivation
- SimultaneousActivation
- StagedActivation

### Experiments

- Scenario
- Experiment
- ParameterGrid
- Multi-seed experiments
- ExperimentResult aggregation

### Data & Reproducibility

- Dataset export
- JSONL export
- CSV export
- Reproducibility manifests
- Snapshot read/write helpers

### Analysis

- SensitivityAnalysis
- Optional SALib integration
- Sobol sampling
- Morris sampling

### Visualization

- plot_timeseries
- plot_multiple_runs
- plot_grid

### Example Gallery

- Wealth model
- Schelling segregation
- Spatial SIR epidemic
- Sugarscape
- Parameter sweep
- GIS example

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/fatihuludag-lab/abmforge.git
cd abmforge
pip install -e ".[dev]"
```

Optional extras:

```bash
pip install -e ".[viz]"
pip install -e ".[analysis]"
pip install -e ".[docs]"
pip install -e ".[all]"
```

## Quick example

<!-- abmforge:execute-python -->
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
        self.record.metric("total_wealth", lambda model: model.agents.sum("wealth"))

    def step(self) -> None:
        self.scheduler.step()


scenario = Scenario(model=WealthModel, seed=42, steps=10)
result = scenario.run()

print(result.dataset.model_records)
```

## Core concepts

ABMForge currently provides:

- `Agent`
- `Model`
- `AgentCollection`
- `Scenario`
- `Experiment`
- `ParameterGrid`
- `ExperimentResult`
- `Recorder`
- `Dataset`
- `Event`
- `EventQueue`

## Spaces

ABMForge supports multiple environment types:

- `GridWorld`
- `NetworkSpace`
- `ContinuousSpace`
- `GISSpace`

## Scheduling

Available activation strategies:

- `SequentialActivation`
- `RandomActivation`
- `SimultaneousActivation`
- `StagedActivation`

## Experiments

ABMForge can run parameter sweeps and repeated-seed experiments:

```python
from abmforge import Experiment

experiment = Experiment(
    model=WealthModel,
    parameters={
        "initial_wealth": [0, 10],
        "growth": [1, 2],
    },
    seeds=[1, 2, 3],
    steps=100,
)

result = experiment.run()

print(result.summary())
result.write_csv("outputs/experiment")
```

## Dataset export

A run dataset can be exported as JSON/JSONL or CSV:

```python
result.dataset.write_json("outputs/run_json")
result.dataset.write_csv("outputs/run_csv")
result.dataset.write_manifest("outputs/run_manifest")
```

Experiment results can also be exported:

```python
experiment_result.write_csv("outputs/experiment")
```

## Reproducibility

ABMForge records run metadata such as:

- run ID
- scenario name
- model name
- parameters
- seed
- status
- start and end timestamps
- executed steps
- stop reason
- Python version
- platform information
- ABMForge version

Snapshot helpers are also available:

```python
from abmforge import read_snapshot, write_snapshot

snapshot = model.snapshot()
write_snapshot(snapshot, "outputs/snapshot.json")

loaded = read_snapshot("outputs/snapshot.json")
```

## Visualization

Visualization helpers are optional and require matplotlib:

```bash
pip install -e ".[viz]"
```

Available helpers:

```python
from abmforge import plot_grid, plot_multiple_runs, plot_timeseries

plot_timeseries(result.dataset, metric="infected")
plot_multiple_runs(experiment_result, metric="mean_wealth")
plot_grid(model.world)
```

## Sensitivity analysis

ABMForge includes a lightweight sensitivity analysis helper:

```python
from abmforge import SensitivityAnalysis

analysis = SensitivityAnalysis(experiment_result, metric="total_wealth")
print(analysis.summary())
```

Optional SALib integration is also available:

```bash
pip install -e ".[analysis]"
```

```python
from abmforge import SALibProblem, sample_sobol, analyze_sobol

problem = SALibProblem(
    bounds={
        "density": (0.4, 0.9),
        "homophily": (0.1, 0.8),
    }
)

samples = sample_sobol(problem, n=128, seed=42)
```

## Examples

The repository includes several examples:

```bash
python3 examples/wealth_model/run.py
python3 examples/schelling/run.py
python3 examples/sir_epidemic/run.py
python3 examples/sugarscape/run.py
python3 examples/parameter_sweep/run.py
python3 examples/gis_space/run.py
```

Current example gallery:

- Wealth model
- Schelling segregation
- Spatial SIR epidemic
- Sugarscape
- Parameter sweep
- GISSpace distance and GeoJSON export

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run local checks:

```bash
ruff format src tests examples
ruff check src tests examples
mypy src
pytest
python3 -m build
```

## API stability

ABMForge is alpha-stage software. The top-level import surface is declared in
`abmforge.api` and documented in `docs/api-stability.md`. Core research
entrypoints such as `Agent`, `Model`, `Scenario`, `Experiment`, `Dataset`, and
`Recorder` are treated as stable-alpha imports; replay, optional analysis, and
visualization helpers remain experimental until their contracts mature.

## Project status

ABMForge is currently an alpha-stage framework.

The current focus is:

- stabilizing public APIs
- improving documentation
- strengthening CI
- expanding examples
- preparing a clean v0.3.0a1 no-publish release-readiness path

## Roadmap

Near-term priorities:

- API stabilization
- documentation site
- example smoke tests in CI
- coverage reporting
- benchmark suite
- stronger replay support
- plugin architecture

## Positioning

ABMForge aims to differentiate through:

- auditable scenario-based runs
- dataset-first outputs
- experiment-native workflows
- explicit event ownership
- multiple space types
- optional visualization and analysis helpers
- lightweight Python-first design

## Contributing

Contributions are welcome.

Good first areas include:

- documentation
- examples
- tests
- schedulers
- spaces
- export formats
- visualization helpers
- analysis tools

Before opening a pull request, please run:

```bash
ruff format src tests examples
ruff check src tests examples
mypy src
pytest
python3 -m build
```

## License

ABMForge is distributed under the Apache-2.0 license. See `LICENSE`.
