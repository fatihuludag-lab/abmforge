import pytest

from abmforge import Agent, GridWorld, Model


class Person(Agent):
    pass


class Parent(Agent):
    pass


def test_agent_has_is_alive_flag():
    model = Model(seed=1)
    agent = model.agents.create(Person, n=1)[0]

    assert agent.is_alive is True


def test_agent_remove_marks_dead_and_removes_from_model():
    model = Model(seed=1)
    agent = model.agents.create(Person, n=1)[0]

    agent.remove()

    assert agent.is_alive is False
    with pytest.raises(KeyError):
        model.agents.get(agent.unique_id)


def test_remove_unknown_agent_raises_key_error():
    model = Model(seed=1)

    with pytest.raises(KeyError):
        model.remove_agent("missing")


def test_agent_spawn_creates_new_agent():
    model = Model(seed=1)
    parent = model.agents.create(Parent, n=1)[0]

    child = parent.spawn(Person, wealth=10)

    assert isinstance(child, Person)
    assert child.wealth == 10
    assert child.model is model


def test_agent_neighbors_delegates_to_world():
    model = Model(seed=1)
    model.world = GridWorld(width=3, height=3, torus=False)

    a = model.agents.create(Person, n=1)[0]
    b = model.agents.create(Person, n=1)[0]

    model.world.place(a, (1, 1))
    model.world.place(b, (1, 2))

    assert b in a.neighbors(radius=1)


def test_agent_neighbors_without_world_raises_runtime_error():
    model = Model(seed=1)
    agent = model.agents.create(Person, n=1)[0]

    with pytest.raises(RuntimeError):
        agent.neighbors()
