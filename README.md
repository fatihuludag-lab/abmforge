# ABMForge

ABMForge is an early-stage, installable Python framework for agent-based simulation.
The first release focuses on a small but usable core:

- `Model`
- `Agent`
- `AgentCollection`
- deterministic RNG via model-level seed
- `GridWorld`
- basic event queue
- `Recorder` and `Dataset`
- `Scenario`
- a minimal CLI

> Status: `0.1.0a1` alpha. Public APIs may still change before `1.0.0`.

## Installation

For users, once published:

```bash
pip install abmforge
```

For local development:

```bash
git clone https://github.com/your-org/abmforge.git
cd abmforge
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## First model

```python
from abmforge import Agent, Model, Scenario


class Person(Agent):
    def step(self) -> None:
        self.wealth += 1


class WealthModel(Model):
    def setup(self) -> None:
        self.agents.create(Person, n=100, wealth=0)
        self.record.metric("total_wealth", lambda m: m.agents.sum("wealth"))

    def step(self) -> None:
        self.agents.shuffle_do("step")


scenario = Scenario(model=WealthModel, seed=42, steps=10)
result = scenario.run()

print(result.dataset.model_records)
```

## Design goals

ABMForge is intended to become:

1. **Installable**: small core package with optional extras.
2. **Reproducible**: every run records seed, parameters, status, and timing.
3. **Experiment-native**: scenarios and experiments are first-class concepts.
4. **Extensible**: future storage, visualization, distributed, and GIS features should be plugins.
5. **Different from Mesa**: dataset-first recording, event ownership, snapshot/replay, and future object/columnar backends.

## Optional extras

```bash
pip install "abmforge[data]"   # pandas, polars, pyarrow
pip install "abmforge[viz]"    # matplotlib
pip install "abmforge[docs]"   # mkdocs
pip install "abmforge[dev]"    # pytest, ruff, mypy, build, twine
```

## CLI

```bash
abmforge --version
abmforge info
```

## Project status

This is the first alpha release. The package is intentionally small. The next milestones are:

- `0.2.0`: stronger ABM examples and grid utilities
- `0.3.0`: event ownership and richer lifecycle hooks
- `0.4.0`: dataset export and storage backend interface
- `0.5.0`: experiment runner and parameter grids
- `1.0.0`: stable public API
