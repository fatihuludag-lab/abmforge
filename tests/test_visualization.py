import matplotlib

matplotlib.use("Agg", force=True)

import pytest

pytest.importorskip("matplotlib")

from abmforge import Agent, Experiment, GridWorld, Model, Scenario
from abmforge.visualization import plot_grid, plot_multiple_runs, plot_timeseries


class DummyAgent(Agent):
    def step(self) -> None:
        self.value += 1


class DummyModel(Model):
    def setup(self) -> None:
        self.agents.create(DummyAgent, n=1, value=0)
        self.record.metric("total", lambda model: model.agents.sum("value"))

    def step(self) -> None:
        self.agents.do("step")


def test_plot_timeseries_returns_axis():
    scenario = Scenario(model=DummyModel, seed=1, steps=3)
    result = scenario.run()

    ax = plot_timeseries(result.dataset, metric="total")

    assert ax.get_xlabel() == "step"
    assert ax.get_ylabel() == "total"


def test_plot_multiple_runs_returns_axis():
    experiment = Experiment(
        model=DummyModel,
        parameters={"a": [1, 2]},
        seeds=[1],
        steps=3,
    )
    result = experiment.run()

    ax = plot_multiple_runs(result, metric="total")

    assert ax.get_xlabel() == "step"
    assert ax.get_ylabel() == "total"


def test_plot_grid_returns_axis():
    model = Model(seed=1)
    model.world = GridWorld(width=3, height=3)

    agent = model.agents.create(DummyAgent, n=1, value=0)[0]
    model.world.place(agent, (1, 1))

    ax = plot_grid(model.world)

    assert ax.get_title() == "GridWorld"
