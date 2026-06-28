# Typed Agents

ABMForge's base `Agent` remains intentionally lightweight and dynamic. This is
useful for teaching, quick experiments, and compact research models. Typed-agent
support is therefore introduced as an additive protocol layer rather than as a
replacement base class.

## What ABMForge provides

The `abmforge.core.protocols` module defines structural typing helpers:

- `AgentID`;
- `AgentLike`;
- `SteppableAgent`;
- `AdvanceableAgent`;
- `StatefulAgent`.

These protocols are useful for type hints, helper functions, tests, and library
extensions that want stronger contracts without forcing every user-defined agent
to inherit from a separate `TypedAgent` class.

## Basic example

```python
from dataclasses import dataclass

from abmforge import Agent, Model, StatefulAgent


@dataclass
class ConsumerState:
    adopted: bool
    threshold: float


class Consumer(Agent):
    state: ConsumerState

    def step(self) -> None:
        if not self.state.adopted and self.rng.random() >= self.state.threshold:
            self.state.adopted = True


def adoption_status(agent: StatefulAgent[ConsumerState]) -> bool:
    return agent.state.adopted


model = Model(seed=42)
consumer = model.agents.create(
    Consumer,
    n=1,
    state=ConsumerState(adopted=False, threshold=0.5),
)[0]

assert adoption_status(consumer) in {False, True}
```

## Collection typing

`AgentCollection.create(...)` and `AgentCollection.by_type(...)` preserve the
concrete agent class in their type signatures. This means typed subclasses can
be created and retrieved without losing their concrete type information in
static type checkers.

```python
consumers = model.agents.create(Consumer, n=10, state=ConsumerState(False, 0.5))
selected = model.agents.by_type(Consumer)
```

## Runtime checks

The protocols are marked with `@runtime_checkable`, so they can be used with
`isinstance(...)` for broad structural checks:

```python
from abmforge import SteppableAgent

assert isinstance(consumer, SteppableAgent)
```

Runtime protocol checks only verify that required attributes or methods are
present. They do not replace static type checking.

## Design boundary

ABMForge does not yet provide a separate `TypedAgent[StateT]` base class. That
would be a stronger architectural commitment and may be considered later. The
current protocol layer is deliberately conservative and backward-compatible.
