import pytest

from abmforge import Agent, ContinuousSpace, Model


class Particle(Agent):
    pass


def test_continuous_space_places_and_moves_agent():
    model = Model(seed=1)
    space = ContinuousSpace(width=10.0, height=10.0)

    agent = model.agents.create(Particle, n=1)[0]
    space.place(agent, (1.0, 2.0))

    assert space.position_of(agent) == (1.0, 2.0)

    space.move(agent, (3.0, 4.0))

    assert space.position_of(agent) == (3.0, 4.0)
    assert agent.pos == (3.0, 4.0)


def test_continuous_space_out_of_bounds_raises():
    model = Model(seed=1)
    space = ContinuousSpace(width=10.0, height=10.0)
    agent = model.agents.create(Particle, n=1)[0]

    with pytest.raises(ValueError):
        space.place(agent, (11.0, 1.0))


def test_continuous_space_torus_wraps_position():
    model = Model(seed=1)
    space = ContinuousSpace(width=10.0, height=10.0, torus=True)
    agent = model.agents.create(Particle, n=1)[0]

    space.place(agent, (11.0, -1.0))

    assert space.position_of(agent) == (1.0, 9.0)


def test_continuous_space_distance():
    model = Model(seed=1)
    space = ContinuousSpace(width=10.0, height=10.0)

    a = model.agents.create(Particle, n=1)[0]
    b = model.agents.create(Particle, n=1)[0]

    space.place(a, (0.0, 0.0))
    space.place(b, (3.0, 4.0))

    assert space.distance(a, b) == 5.0


def test_continuous_space_neighbors():
    model = Model(seed=1)
    space = ContinuousSpace(width=10.0, height=10.0)

    a = model.agents.create(Particle, n=1)[0]
    b = model.agents.create(Particle, n=1)[0]
    c = model.agents.create(Particle, n=1)[0]

    space.place(a, (0.0, 0.0))
    space.place(b, (1.0, 1.0))
    space.place(c, (9.0, 9.0))

    assert b in space.neighbors(a, radius=2.0)
    assert c not in space.neighbors(a, radius=2.0)
