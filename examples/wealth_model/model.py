from __future__ import annotations

from abmforge import Agent, Model


class Person(Agent):
    def step(self) -> None:
        self.wealth += 1


class WealthModel(Model):
    def setup(self) -> None:
        self.agents.create(Person, n=int(self.parameters.get("n", 100)), wealth=0)
        self.record.metric("total_wealth", lambda m: m.agents.sum("wealth"))
        self.record.metric("mean_wealth", lambda m: m.agents.mean("wealth"))

    def step(self) -> None:
        self.agents.shuffle_do("step")
