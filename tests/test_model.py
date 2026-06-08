from __future__ import annotations

from abmforge import Agent, Model


class CounterAgent(Agent):
    def step(self) -> None:
        self.value += 1


class CounterModel(Model):
    def setup(self) -> None:
        self.agents.create(CounterAgent, n=3, value=0)
        self.record.metric("total", lambda m: m.agents.sum("value"))

    def step(self) -> None:
        self.agents.do("step")


def test_model_run_for_steps_and_records() -> None:
    model = CounterModel(seed=1)
    model.setup()
    model.run_for(5)

    assert model.steps == 5
    assert model.time == 5.0
    assert model.agents.sum("value") == 15
    assert model.record.dataset.model_records[-1]["value"] == 15.0


def test_stop() -> None:
    class StopModel(CounterModel):
        def step(self) -> None:
            super().step()
            self.stop("done")

    model = StopModel(seed=1)
    model.setup()
    model.run_for(10)

    assert model.steps == 1
    assert model.stop_reason == "done"
    assert model.status == "stopped"
