# Getting Started

## Installation

Clone the repository:

```bash
git clone https://github.com/fatihuludag-lab/abmforge.git
cd abmforge
```

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Optional extras:

```bash
pip install -e ".[viz]"
pip install -e ".[analysis]"
pip install -e ".[docs]"
```

## First Scenario

```python
from abmforge import Scenario

scenario = Scenario(
    model=MyModel,
    seed=42,
    steps=100,
)

result = scenario.run()
```

## Dataset Export

```python
result.dataset.write_csv("outputs/run")
```

## Experiment

```python
from abmforge import Experiment

experiment = Experiment(
    model=MyModel,
    parameters={
        "alpha": [0.1, 0.5],
        "beta": [1, 2],
    },
    seeds=[1, 2, 3],
    steps=100,
)

result = experiment.run()
```

## Visualization

```python
from abmforge import plot_timeseries

plot_timeseries(
    result.dataset,
    metric="population",
)
```

## Examples

Run the bundled examples:

```bash
python3 examples/schelling/run.py
python3 examples/sir_epidemic/run.py
python3 examples/sugarscape/run.py
python3 examples/parameter_sweep/run.py
python3 examples/gis_space/run.py
```
