from abmforge import Agent, Experiment, Model, SensitivityAnalysis


class GrowthAgent(Agent):
    def step(self) -> None:
        self.value += self.model.parameters["growth"]


class GrowthModel(Model):
    def setup(self) -> None:
        self.agents.create(GrowthAgent, n=1, value=0)
        self.record.metric("total", lambda model: model.agents.sum("value"))

    def step(self) -> None:
        self.agents.do("step")


def test_sensitivity_analysis_final_metric_by_run():
    experiment = Experiment(
        model=GrowthModel,
        parameters={"growth": [1, 2]},
        seeds=[1],
        steps=3,
    )

    result = experiment.run()
    analysis = SensitivityAnalysis(result, metric="total")

    final_values = analysis.final_metric_by_run()

    assert len(final_values) == 2
    assert sorted(final_values.values()) == [3.0, 6.0]


def test_sensitivity_analysis_parameter_effects():
    experiment = Experiment(
        model=GrowthModel,
        parameters={"growth": [1, 2]},
        seeds=[1, 2],
        steps=3,
    )

    result = experiment.run()
    analysis = SensitivityAnalysis(result, metric="total")

    effects = analysis.parameter_effects()

    assert effects["growth"]["1"] == 3.0
    assert effects["growth"]["2"] == 6.0


def test_sensitivity_analysis_ranking():
    experiment = Experiment(
        model=GrowthModel,
        parameters={
            "growth": [1, 2],
            "noise": [0, 1],
        },
        seeds=[1],
        steps=3,
    )

    result = experiment.run()
    analysis = SensitivityAnalysis(result, metric="total")

    ranking = analysis.rank()

    assert ranking[0]["parameter"] == "growth"
    assert ranking[0]["sensitivity"] == 3.0


def test_sensitivity_analysis_summary():
    experiment = Experiment(
        model=GrowthModel,
        parameters={"growth": [1, 2]},
        seeds=[1],
        steps=3,
    )

    result = experiment.run()
    analysis = SensitivityAnalysis(result, metric="total")

    summary = analysis.summary()

    assert summary["metric"] == "total"
    assert "effects" in summary
    assert "ranking" in summary
