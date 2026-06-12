from abmforge import Agent, Model
from abmforge.scheduling import (
    RandomActivation,
    SequentialActivation,
    SimultaneousActivation,
    StagedActivation,
)


class CounterAgent(Agent):
    def step(self) -> None:
        self.count += 1

    def advance(self) -> None:
        self.count += 10

    def sense(self) -> None:
        self.trace.append("sense")

    def decide(self) -> None:
        self.trace.append("decide")

    def act(self) -> None:
        self.trace.append("act")


def test_sequential_activation_steps_all_agents():
    model = Model(seed=1)
    model.agents.create(CounterAgent, n=3, count=0)

    scheduler = SequentialActivation(model)
    scheduler.step()

    assert [agent.count for agent in model.agents] == [1, 1, 1]


def test_random_activation_steps_all_agents():
    model = Model(seed=1)
    model.agents.create(CounterAgent, n=3, count=0)

    scheduler = RandomActivation(model)
    scheduler.step()

    assert sorted(agent.count for agent in model.agents) == [1, 1, 1]


def test_simultaneous_activation_calls_step_and_advance():
    model = Model(seed=1)
    model.agents.create(CounterAgent, n=2, count=0)

    scheduler = SimultaneousActivation(model)
    scheduler.step()

    assert [agent.count for agent in model.agents] == [11, 11]


def test_staged_activation_calls_stages_in_order():
    model = Model(seed=1)
    for agent in model.agents.create(CounterAgent, n=2):
        agent.trace = []

    scheduler = StagedActivation(
        model,
        stages=["sense", "decide", "act"],
        shuffle=False,
    )
    scheduler.step()

    for agent in model.agents:
        assert agent.trace == ["sense", "decide", "act"]


def test_staged_activation_can_shuffle_agents():
    model = Model(seed=1)
    for agent in model.agents.create(CounterAgent, n=5):
        agent.trace = []

    scheduler = StagedActivation(
        model,
        stages=["sense", "decide"],
        shuffle=True,
    )
    scheduler.step()

    for agent in model.agents:
        assert agent.trace == ["sense", "decide"]
