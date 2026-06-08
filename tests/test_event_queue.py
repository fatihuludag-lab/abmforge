from __future__ import annotations

from abmforge import Agent, Model


class Person(Agent):
    pass


def test_schedule_and_execute_event() -> None:
    model = Model(seed=1)
    model.hit = 0

    def callback() -> None:
        model.hit += 1

    model.events.schedule(after=0, callback=callback, tags=["test"])
    executed = model.events.process_due(time=0)

    assert executed == 1
    assert model.hit == 1
    assert model.record.dataset.event_records[-1]["status"] == "executed"


def test_cancel_event() -> None:
    model = Model(seed=1)
    model.hit = 0

    def callback() -> None:
        model.hit += 1

    event = model.events.schedule(after=0, callback=callback)
    assert model.events.cancel(event.event_id) is True
    executed = model.events.process_due(time=0)

    assert executed == 0
    assert model.hit == 0


def test_cancel_by_owner_when_agent_removed() -> None:
    model = Model(seed=1)
    agent = model.agents.create(Person)[0]
    model.hit = 0

    def callback() -> None:
        model.hit += 1

    model.events.schedule(after=1, callback=callback, owner=agent.unique_id, tags=["owned"])
    assert model.events.pending_count() == 1

    model.remove_agent(agent)

    assert model.events.pending_count() == 0
    model.events.process_due(time=1)
    assert model.hit == 0
