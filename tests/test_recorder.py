from __future__ import annotations

from abmforge import Agent, Model


class Person(Agent):
    def step(self) -> None:
        self.wealth += 1


class WealthModel(Model):
    def setup(self) -> None:
        self.agents.create(Person, n=2, wealth=0)
        self.record.metric("total_wealth", lambda m: m.agents.sum("wealth"))
        self.record.agent("wealth")

    def step(self) -> None:
        self.agents.do("step")


def test_recorder_collects_model_and_agent_records() -> None:
    model = WealthModel(seed=1)
    model.setup()
    model.run_for(2)

    assert len(model.record.dataset.model_records) == 2
    assert len(model.record.dataset.agent_records) == 4
    assert model.record.dataset.model_records[-1]["value"] == 4.0
