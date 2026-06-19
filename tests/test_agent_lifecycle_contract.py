from __future__ import annotations

import pytest

from abmforge.core.agent import Agent
from abmforge.core.agent_lifecycle import (
    ACTIVE,
    REMOVED,
    VALID_AGENT_LIFECYCLE_STATUSES,
    validate_agent_lifecycle_status,
)
from abmforge.core.model import Model
from abmforge.world import GridWorld


class LifecycleAgent(Agent):
    def step(self) -> None:
        pass


def test_agent_initial_lifecycle_status_is_active() -> None:
    model = Model()
    agent = model.agents.create(LifecycleAgent, n=1)[0]

    assert agent.is_alive is True
    assert agent.lifecycle_status == ACTIVE


def test_valid_agent_lifecycle_statuses_are_explicit() -> None:
    assert {
        ACTIVE,
        REMOVED,
    } == VALID_AGENT_LIFECYCLE_STATUSES


def test_validate_agent_lifecycle_status_accepts_known_status() -> None:
    assert validate_agent_lifecycle_status(ACTIVE) == ACTIVE
    assert validate_agent_lifecycle_status(REMOVED) == REMOVED


def test_validate_agent_lifecycle_status_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="Invalid agent lifecycle status"):
        validate_agent_lifecycle_status("unknown")


def test_agent_remove_marks_agent_removed_and_removes_from_collection() -> None:
    model = Model()
    agent = model.agents.create(LifecycleAgent, n=1)[0]

    agent.remove()

    assert agent.is_alive is False
    assert agent.lifecycle_status == REMOVED
    assert agent.unique_id not in model.agents

    with pytest.raises(KeyError):
        model.agents.get(agent.unique_id)


def test_agent_remove_removes_agent_from_world() -> None:
    model = Model()
    model.world = GridWorld(5, 5)
    agent = model.agents.create(LifecycleAgent, n=1)[0]

    model.world.place(agent, (2, 2))

    assert model.world.position_of(agent) == (2, 2)
    assert agent.pos == (2, 2)

    agent.remove()

    assert agent.is_alive is False
    assert agent.lifecycle_status == REMOVED
    assert not hasattr(agent, "pos")

    with pytest.raises(KeyError):
        model.world.position_of(agent)


def test_agent_remove_cancels_owned_pending_events() -> None:
    model = Model()
    agent = model.agents.create(LifecycleAgent, n=1)[0]

    called = {"value": False}

    model.events.schedule(
        callback=lambda: called.__setitem__("value", True),
        after=1.0,
        owner=agent.unique_id,
    )

    assert model.events.pending_count() == 1

    agent.remove()

    assert model.events.pending_count() == 0

    model.events.process_due(time=10.0)

    assert called["value"] is False


def test_agent_remove_records_lifecycle_event() -> None:
    model = Model()
    agent = model.agents.create(LifecycleAgent, n=1)[0]

    agent.remove()

    records = model.record.dataset.lifecycle_records

    assert records[-1]["event"] == "agent_removed"
    assert records[-1]["agent_id"] == agent.unique_id
    assert records[-1]["run_id"] == model.run_id


def test_agent_remove_records_cancelled_event_transition() -> None:
    model = Model()
    agent = model.agents.create(LifecycleAgent, n=1)[0]

    event = model.events.schedule(
        callback=lambda: None,
        after=1.0,
        owner=agent.unique_id,
        tags=["owned"],
    )

    agent.remove()

    records = model.record.dataset.event_records

    assert any(
        record["event_id"] == event.event_id
        and record["owner"] == agent.unique_id
        and record["status"] == "cancelled"
        for record in records
    )


def test_model_remove_agent_accepts_agent_id() -> None:
    model = Model()
    agent = model.agents.create(LifecycleAgent, n=1)[0]

    model.remove_agent(agent.unique_id)

    assert agent.is_alive is False
    assert agent.lifecycle_status == REMOVED
    assert agent.unique_id not in model.agents


def test_removing_unknown_agent_raises_key_error() -> None:
    model = Model()

    with pytest.raises(KeyError, match="unknown agent id"):
        model.remove_agent(999)
