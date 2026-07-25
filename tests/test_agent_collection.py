from __future__ import annotations

import pytest

from abmforge.core.agent import Agent
from abmforge.core.model import Model


class Person(Agent):
    def step(self) -> None:
        self.wealth += 1


def test_create_count_and_aggregate() -> None:
    model = Model(seed=42)
    created = model.agents.create(Person, n=4, wealth=2)

    assert len(created) == 4
    assert model.agents.count() == 4
    assert model.agents.sum("wealth") == 8.0
    assert model.agents.mean("wealth") == 2.0


def test_shuffle_do_is_seed_deterministic() -> None:
    class OrderAgent(Agent):
        def step(self) -> None:
            self.model.order.append(self.unique_id)

    def run_once() -> list[int | str]:
        model = Model(seed=123)
        model.order = []
        model.agents.create(OrderAgent, n=5)
        model.agents.shuffle_do("step")
        return model.order

    assert run_once() == run_once()


def test_where_and_count_where() -> None:
    model = Model(seed=42)
    model.agents.create(Person, n=2, wealth=1, state="a")
    model.agents.create(Person, n=3, wealth=2, state="b")

    assert len(model.agents.where(state="a")) == 2
    assert model.agents.count_where(state="b") == 3


def test_collection_rejects_agent_from_another_model() -> None:
    first_model = Model()
    second_model = Model()

    foreign_agent = Agent(
        model=first_model,
        unique_id=1,
    )

    with pytest.raises(
        ValueError,
        match="belongs to another model",
    ):
        second_model.agents.add(foreign_agent)

    assert len(second_model.agents) == 0


def test_collection_contains_checks_agent_identity() -> None:
    first_model = Model()
    second_model = Model()

    local_agent = Agent(
        model=first_model,
        unique_id=1,
    )
    foreign_agent = Agent(
        model=second_model,
        unique_id=1,
    )

    first_model.agents.add(local_agent)

    assert local_agent in first_model.agents
    assert foreign_agent not in first_model.agents
    assert 1 in first_model.agents


def test_collection_remove_rejects_foreign_agent_with_same_id() -> None:
    first_model = Model()
    second_model = Model()

    local_agent = Agent(
        model=first_model,
        unique_id=1,
    )
    foreign_agent = Agent(
        model=second_model,
        unique_id=1,
    )

    first_model.agents.add(local_agent)

    with pytest.raises(
        ValueError,
        match="does not belong to this collection",
    ):
        first_model.agents.remove(foreign_agent)

    assert first_model.agents.get(1) is local_agent
