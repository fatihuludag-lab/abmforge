from abmforge import Agent, Model, NetworkSpace


class Person(Agent):
    pass


def test_network_space_places_and_finds_neighbors():
    model = Model(seed=1)
    a = model.agents.create(Person, n=1)[0]
    b = model.agents.create(Person, n=1)[0]

    space = NetworkSpace()
    space.add_edge("x", "y")
    space.place_agent(a, "x")
    space.place_agent(b, "y")

    assert space.position_of(a) == "x"
    assert space.neighbors(a) == [b]


def test_network_space_moves_agent():
    model = Model(seed=1)
    a = model.agents.create(Person, n=1)[0]

    space = NetworkSpace()
    space.add_edge("x", "y")
    space.place_agent(a, "x")
    space.move_agent(a, "y")

    assert space.position_of(a) == "y"
    assert space.agents_at("y") == [a]
