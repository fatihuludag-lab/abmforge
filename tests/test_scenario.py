from __future__ import annotations

from abmforge import Agent, Model, Scenario


class Person(Agent):
    def step(self) -> None:
        self.wealth += 1


class WealthModel(Model):
    def setup(self) -> None:
        self.agents.create(Person, n=int(self.parameters.get("n", 3)), wealth=0)
        self.record.metric("total_wealth", lambda m: m.agents.sum("wealth"))

    def step(self) -> None:
        self.agents.shuffle_do("step")


def test_scenario_run_metadata() -> None:
    result = Scenario(model=WealthModel, parameters={"n": 3}, seed=42, steps=4).run()

    assert result.steps == 4
    assert result.status == "completed"
    assert result.dataset.runs[0]["seed"] == 42
    assert result.dataset.runs[0]["parameters"] == {"n": 3}
    assert result.dataset.model_records[-1]["value"] == 12.0


def test_same_seed_same_records() -> None:
    scenario = Scenario(model=WealthModel, parameters={"n": 5}, seed=123, steps=3)

    r1 = scenario.run()
    r2 = scenario.run()

    values_1 = [record["value"] for record in r1.dataset.model_records]
    values_2 = [record["value"] for record in r2.dataset.model_records]
    assert values_1 == values_2
