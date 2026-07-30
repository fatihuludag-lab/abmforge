# Spaces

> **Normative semantics:** Built-in placement, movement, identity, and
> removal guarantees are defined in
> [Simulation Semantics V1](simulation-semantics-v1.md).

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

## Referential-integrity contract

`GridWorld`, `ContinuousSpace`, `GISSpace`, and `NetworkSpace` use a shared
referential-integrity contract.

A placed identifier refers to the same agent object stored in the space.
An object with the same identifier but a different object cannot inspect,
move, remove, or replace the placed agent.

An agent that already belongs to another space cannot be placed into a second
built-in space before spatial removal from the first space.

Successful removal from a built-in space clears all position, occupancy,
node, and identity indexes. Built-in spaces clear both `agent.pos` and `agent.world` after successful removal.

`space.remove(agent)` is spatial unplacement only. It does not change
collection membership, lifecycle status, owned events, or lifecycle records.

For complete lifecycle removal, use `AgentCollection.remove(...)` or
`Model.remove_agent(...)`.

A failed placement or removal request leaves existing indexes unchanged when
referential-integrity validation rejects the request.

`NetworkSpace.place(...)` may move the same already-placed agent object to
another node. A different object using the same identifier is rejected.

## Choosing a Space

| Space | Best for |
|---|---|
| `GridWorld` | discrete spatial ABMs |
| `NetworkSpace` | relational and network ABMs |
| `ContinuousSpace` | continuous movement |
| `GISSpace` | geographic coordinate models |
