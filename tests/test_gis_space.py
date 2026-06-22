from abmforge import Agent, GISSpace, Model


class Person(Agent):
    pass


def test_gis_space_distance():
    model = Model(seed=1)

    a = model.agents.create(Person, n=1)[0]
    b = model.agents.create(Person, n=1)[0]

    space = GISSpace()

    space.place(a, (32.8597, 39.9334))
    space.place(b, (29.0, 41.0))

    distance = space.distance(a, b)

    assert distance > 0


def test_gis_neighbors():
    model = Model(seed=1)

    a = model.agents.create(Person, n=1)[0]
    b = model.agents.create(Person, n=1)[0]

    space = GISSpace()

    space.place(a, (35.0, 39.0))
    space.place(b, (35.01, 39.01))

    neighbors = space.neighbors(a, radius_km=5)

    assert b in neighbors


def test_geojson_export():
    model = Model(seed=1)

    agent = model.agents.create(Person, n=1)[0]

    space = GISSpace()
    space.place(agent, (35.0, 39.0))

    geojson = space.to_geojson()

    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 1


def test_gis_agents_at_returns_agents_in_placement_order():
    model = Model(seed=1)
    a = model.agents.create(Person, n=1)[0]
    b = model.agents.create(Person, n=1)[0]
    space = GISSpace()

    position = (35.0, 39.0)
    space.place(a, position)
    space.place(b, position)

    assert space.agents_at(position) == [a, b]


def test_gis_neighbors_accept_position_query():
    model = Model(seed=1)
    near = model.agents.create(Person, n=1)[0]
    far = model.agents.create(Person, n=1)[0]
    space = GISSpace()

    space.place(near, (35.01, 39.01))
    space.place(far, (45.0, 45.0))

    neighbors = space.neighbors((35.0, 39.0), radius_km=5)

    assert near in neighbors
    assert far not in neighbors
