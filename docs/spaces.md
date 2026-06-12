# Spaces

ABMForge supports several environment types for agent interaction.

## GridWorld

`GridWorld` is a two-dimensional discrete grid.

It is useful for:

- segregation models
- epidemic models
- cellular models
- resource landscapes

```python
from abmforge import GridWorld

world = GridWorld(
    width=20,
    height=20,
    torus=True,
    multi=False,
)

world.place(agent, (5, 5))
world.move(agent, (6, 5))

neighbors = world.neighbors(
    agent,
    radius=1,
    include_center=False,
)
```

## NetworkSpace

`NetworkSpace` supports graph-based agent interaction.

It is useful for:

- social networks
- contagion models
- opinion dynamics
- information diffusion

```python
from abmforge import NetworkSpace

space = NetworkSpace()
space.add_edge("a", "b")
space.place(agent, "a")
```

## ContinuousSpace

`ContinuousSpace` supports continuous two-dimensional coordinates.

It is useful for:

- mobility models
- swarm models
- ecology models
- evacuation models

```python
from abmforge import ContinuousSpace

space = ContinuousSpace(
    width=100.0,
    height=100.0,
    torus=True,
)
```

## GISSpace

`GISSpace` supports longitude-latitude coordinates and distance queries.

It is useful for:

- urban simulation
- mobility studies
- spatial epidemiology
- transportation models

```python
from abmforge import GISSpace

space = GISSpace()
space.place(agent, (32.8597, 39.9334))

distance_km = space.distance(agent_a, agent_b)
geojson = space.to_geojson()
```

## Choosing a Space

| Space | Best for |
|---|---|
| `GridWorld` | discrete spatial ABMs |
| `NetworkSpace` | relational and network ABMs |
| `ContinuousSpace` | continuous movement |
| `GISSpace` | geographic coordinate models |
