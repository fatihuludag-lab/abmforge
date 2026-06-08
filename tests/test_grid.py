from __future__ import annotations

from abmforge import Agent, GridWorld, Model


class Person(Agent):
    pass


def test_place_move_remove() -> None:
    model = Model(seed=1)
    agent = model.agents.create(Person)[0]
    world = GridWorld(5, 5)
    model.world = world

    world.place(agent, (1, 1))
    assert world.position_of(agent) == (1, 1)
    assert world.agents_at((1, 1)) == [agent]

    world.move(agent, (2, 1))
    assert world.position_of(agent) == (2, 1)
    assert world.agents_at((1, 1)) == []

    world.remove(agent)
    assert world.agents_at((2, 1)) == []


def test_torus_neighbors() -> None:
    model = Model(seed=1)
    a, b = model.agents.create(Person, n=2)
    world = GridWorld(5, 5, torus=True)

    world.place(a, (0, 0))
    world.place(b, (4, 4))

    assert b in world.neighbors(a, radius=1)
