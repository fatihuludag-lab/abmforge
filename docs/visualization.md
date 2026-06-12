# Visualization

Visualization helpers are optional and require matplotlib.

Install visualization dependencies:

```bash
pip install -e ".[viz]"
```

## Time Series

```python
from abmforge import plot_timeseries

plot_timeseries(
    result.dataset,
    metric="infected",
)
```

## Multiple Runs

```python
from abmforge import plot_multiple_runs

plot_multiple_runs(
    experiment_result,
    metric="mean_wealth",
)
```

## GridWorld

```python
from abmforge import plot_grid

plot_grid(model.world)
```

## Notes

Visualization helpers are intentionally lightweight. They are designed for quick inspection and teaching workflows rather than publication-ready figures.
