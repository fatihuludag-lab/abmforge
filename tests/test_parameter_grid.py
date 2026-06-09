from abmforge import Agent, Experiment, Model, ParameterGrid


class DummyAgent(Agent):
    def step(self) -> None:
        self.value += 1


class DummyModel(Model):
    def setup(self) -> None:
        self.agents.create(DummyAgent, n=1, value=0)
        self.record.metric("total", lambda model: model.agents.sum("value"))

    def step(self) -> None:
        self.agents.do("step")


def test_parameter_grid_generates_cartesian_product():
    grid = ParameterGrid(
        {
            "density": [0.6, 0.8],
            "homophily": [0.3, 0.5],
        }
    )

    combinations = list(grid)

    assert len(combinations) == 4
    assert {"density": 0.6, "homophily": 0.3} in combinations
    assert {"density": 0.8, "homophily": 0.5} in combinations


def test_parameter_grid_len():
    grid = ParameterGrid(
        {
            "a": [1, 2, 3],
            "b": [10, 20],
        }
    )

    assert len(grid) == 6


def test_experiment_generates_scenarios_from_grid_and_seeds():
    experiment = Experiment(
        model=DummyModel,
        parameters={"a": [1, 2], "b": [3]},
        seeds=[10, 20],
        steps=1,
        name="grid-test",
    )

    scenarios = experiment.scenarios()

    assert len(scenarios) == 4
    assert scenarios[0].name == "grid-test"


def test_experiment_runs_all_scenarios():
    experiment = Experiment(
        model=DummyModel,
        parameters={"a": [1, 2]},
        seeds=[10, 20],
        steps=2,
    )

    result = experiment.run()

    assert len(result) == 4
    assert result.run_count == 4
    assert len(result.successful()) == 4
    assert all(run.steps == 2 for run in result)


def test_experiment_still_supports_explicit_scenarios():
    scenarios = [
        Experiment(
            model=DummyModel,
            parameters={"a": [1]},
            seeds=[1],
            steps=1,
        ).scenarios()[0]
    ]

    experiment = Experiment(scenarios=scenarios)
    result = experiment.run()

    assert result.run_count == 1
