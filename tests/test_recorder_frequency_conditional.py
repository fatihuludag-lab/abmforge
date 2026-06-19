import pytest

from abmforge.core.agent import Agent
from abmforge.core.model import Model


class RecordingAgent(Agent):
    pass


class RecordingModel(Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0

    def step(self) -> None:
        self.counter += 1

        for agent in self.agents:
            if hasattr(agent, "wealth"):
                agent.wealth += 1


def test_metric_every_records_only_matching_steps() -> None:
    model = RecordingModel()
    model.record.metric("counter", lambda m: m.counter, every=2)

    model.run_for(5)

    records = model.record.dataset.model_records

    assert [record["step"] for record in records] == [2, 4]
    assert [record["value"] for record in records] == [2, 4]


def test_metric_when_records_only_when_predicate_is_true() -> None:
    model = RecordingModel()
    model.record.metric(
        "counter",
        lambda m: m.counter,
        when=lambda m: m.steps >= 3,
    )

    model.run_for(4)

    records = model.record.dataset.model_records

    assert [record["step"] for record in records] == [3, 4]
    assert [record["value"] for record in records] == [3, 4]


def test_metric_every_and_when_can_be_combined() -> None:
    model = RecordingModel()
    model.record.metric(
        "counter",
        lambda m: m.counter,
        every=2,
        when=lambda m: m.steps >= 3,
    )

    model.run_for(6)

    records = model.record.dataset.model_records

    assert [record["step"] for record in records] == [4, 6]
    assert [record["value"] for record in records] == [4, 6]


def test_agent_every_records_only_matching_steps() -> None:
    model = RecordingModel()
    model.agents.create(RecordingAgent, n=2, wealth=0)
    model.record.agent("wealth", every=2)

    model.run_for(3)

    records = model.record.dataset.agent_records

    assert len(records) == 2
    assert {record["step"] for record in records} == {2}
    assert [record["value"] for record in records] == [2, 2]


def test_agent_when_records_only_when_model_predicate_is_true() -> None:
    model = RecordingModel()
    model.agents.create(RecordingAgent, n=1, wealth=0)
    model.record.agent("wealth", when=lambda m: m.steps >= 2)

    model.run_for(3)

    records = model.record.dataset.agent_records

    assert [record["step"] for record in records] == [2, 3]
    assert [record["value"] for record in records] == [2, 3]


def test_agent_where_records_only_matching_agents() -> None:
    model = RecordingModel()
    model.agents.create(RecordingAgent, n=1, wealth=0, group="treated")
    model.agents.create(RecordingAgent, n=1, wealth=0, group="control")
    model.record.agent(
        "wealth",
        where=lambda agent: agent.group == "treated",
    )

    model.run_for(2)

    records = model.record.dataset.agent_records

    assert len(records) == 2
    assert {record["agent_id"] for record in records} == {1}
    assert [record["value"] for record in records] == [1, 2]


def test_agent_every_when_and_where_can_be_combined() -> None:
    model = RecordingModel()
    model.agents.create(RecordingAgent, n=1, wealth=0, group="treated")
    model.agents.create(RecordingAgent, n=1, wealth=0, group="control")
    model.record.agent(
        "wealth",
        every=2,
        when=lambda m: m.steps >= 2,
        where=lambda agent: agent.group == "treated",
    )

    model.run_for(5)

    records = model.record.dataset.agent_records

    assert [record["step"] for record in records] == [2, 4]
    assert {record["agent_id"] for record in records} == {1}
    assert [record["value"] for record in records] == [2, 4]


@pytest.mark.parametrize("every", [0, -1, True])
def test_metric_rejects_invalid_every(every) -> None:
    model = RecordingModel()

    with pytest.raises(ValueError, match="every must be a positive integer"):
        model.record.metric("counter", lambda m: m.counter, every=every)


@pytest.mark.parametrize("every", [0, -1, False])
def test_agent_rejects_invalid_every(every) -> None:
    model = RecordingModel()

    with pytest.raises(ValueError, match="every must be a positive integer"):
        model.record.agent("wealth", every=every)
