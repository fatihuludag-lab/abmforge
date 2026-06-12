from __future__ import annotations

from abmforge import Agent, GISSpace, Model


class CityAgent(Agent):
    pass


model = Model(seed=42)

ankara = model.agents.create(CityAgent, n=1)[0]
istanbul = model.agents.create(CityAgent, n=1)[0]

space = GISSpace()

space.place(ankara, (32.8597, 39.9334))
space.place(istanbul, (28.9784, 41.0082))

print(f"Distance: {space.distance(ankara, istanbul):.2f} km")

print(space.to_geojson())
