from __future__ import annotations

import pytest

from abmforge import Agent, Model


class Person(Agent):
    pass


def test_from_snapshot_preserves_custom_agent_class_with_registry() -> None:
    model = Model(seed=42)
    original = model.agents.create(Person, n=1, wealth=10)[0]

    restored = Model.from_snapshot(
        model.snapshot(),
        agent_classes={"Person": Person},
    )

    restored_agent = restored.agents.get(original.unique_id)

    assert isinstance(restored_agent, Person)
    assert restored_agent.unique_id == original.unique_id
    assert restored_agent.wealth == 10


def test_from_snapshot_requires_registry_for_custom_agent_types() -> None:
    model = Model(seed=42)
    model.agents.create(Person, n=1, wealth=10)

    with pytest.raises(ValueError, match="agent type 'Person'"):
        Model.from_snapshot(model.snapshot())


def test_from_snapshot_keeps_next_integer_id_after_restore() -> None:
    model = Model(seed=42)
    model.agents.create(Person, n=2, wealth=10)

    restored = Model.from_snapshot(
        model.snapshot(),
        agent_classes={"Person": Person},
    )
    new_agent = restored.agents.create(Person, n=1, wealth=99)[0]

    assert new_agent.unique_id == 3
    assert new_agent.wealth == 99


def test_agent_collection_add_updates_next_integer_id() -> None:
    model = Model(seed=42)
    model.agents.add(Agent(model=model, unique_id=10))

    new_agent = model.agents.create(Agent, n=1)[0]

    assert new_agent.unique_id == 11
