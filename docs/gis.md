# GISSpace

`GISSpace` is a lightweight geographic space for longitude-latitude coordinates.

It is designed for:

- urban simulation
- transportation models
- mobility studies
- spatial epidemiology
- geographic agent placement

## Basic Usage

```python
from abmforge import Agent, GISSpace, Model


class CityAgent(Agent):
    pass


model = Model(seed=42)
ankara = model.agents.create(CityAgent, n=1)[0]
istanbul = model.agents.create(CityAgent, n=1)[0]

space = GISSpace()
space.place(ankara, (32.8597, 39.9334))
space.place(istanbul, (28.9784, 41.0082))

distance = space.distance(ankara, istanbul)
```

## GeoJSON Export

```python
geojson = space.to_geojson()
```

## Current Scope

`GISSpace` currently supports:

- point coordinates
- haversine distance
- radius-based neighbor queries
- GeoJSON point export

Future versions may support:

- GeoPandas integration
- shapefile loading
- polygon containment
- routing
- raster data
