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
