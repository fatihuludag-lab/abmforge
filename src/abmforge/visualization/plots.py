from __future__ import annotations

from typing import Any


def _require_matplotlib() -> Any:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Visualization helpers require matplotlib. Install it with: pip install matplotlib"
        ) from exc

    return plt


def plot_timeseries(
    dataset: Any,
    *,
    metric: str,
    ax: Any | None = None,
) -> Any:
    """Plot one model-level metric over time for a single run."""
    plt = _require_matplotlib()

    records = [record for record in dataset.model_records if record.get("metric") == metric]

    if ax is None:
        _, ax = plt.subplots()

    steps = [record["step"] for record in records]
    values = [record["value"] for record in records]

    ax.plot(steps, values)
    ax.set_xlabel("step")
    ax.set_ylabel(metric)
    ax.set_title(metric)

    return ax


def plot_multiple_runs(
    experiment_result: Any,
    *,
    metric: str,
    ax: Any | None = None,
) -> Any:
    """Plot one metric across all runs in an experiment result."""
    plt = _require_matplotlib()

    if ax is None:
        _, ax = plt.subplots()

    for run in experiment_result:
        records = [record for record in run.dataset.model_records if record.get("metric") == metric]

        steps = [record["step"] for record in records]
        values = [record["value"] for record in records]

        label = run.run_id
        ax.plot(steps, values, label=label)

    ax.set_xlabel("step")
    ax.set_ylabel(metric)
    ax.set_title(metric)

    return ax


def plot_grid(
    world: Any,
    *,
    ax: Any | None = None,
    value_getter: Any | None = None,
) -> Any:
    """Plot agent counts or custom cell values from a GridWorld."""
    plt = _require_matplotlib()

    if ax is None:
        _, ax = plt.subplots()

    grid: list[list[float]] = []

    for y in range(world.height):
        row = []
        for x in range(world.width):
            position = (x, y)

            if value_getter is None:
                value = len(world.agents_at(position))
            else:
                value = value_getter(world, position)

            row.append(float(value))
        grid.append(row)

    ax.imshow(grid, origin="lower")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("GridWorld")

    return ax
