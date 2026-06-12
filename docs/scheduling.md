# Scheduling

Scheduling controls the order in which agents act.

ABMForge provides several activation strategies.

## SequentialActivation

Activates agents in insertion order.

```python
from abmforge.scheduling import SequentialActivation

self.scheduler = SequentialActivation(self)
```

## RandomActivation

Activates agents in a deterministic random order using the model-level RNG.

```python
from abmforge.scheduling import RandomActivation

self.scheduler = RandomActivation(self)
```

## SimultaneousActivation

Calls `step()` for all agents, then calls `advance()` for agents that define it.

```python
from abmforge.scheduling import SimultaneousActivation

self.scheduler = SimultaneousActivation(self)
```

## StagedActivation

Calls named methods on agents in a specified order.

```python
from abmforge.scheduling import StagedActivation

self.scheduler = StagedActivation(
    self,
    stages=["sense", "decide", "act"],
    shuffle=True,
)
```

## Choosing a Scheduler

| Scheduler | Use when |
|---|---|
| `SequentialActivation` | deterministic ordering is desired |
| `RandomActivation` | random activation is part of the model assumption |
| `SimultaneousActivation` | agents should update together |
| `StagedActivation` | behavior has explicit phases |
