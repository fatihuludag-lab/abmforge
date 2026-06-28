# Scheduling

Scheduling controls the order in which agents act.

Activation order is a modelling assumption. In agent-based modelling, changing the scheduler can change the simulation result. ABMForge therefore treats schedulers as explicit model components.

## Built-in schedulers

| Scheduler | Activation order | Uses model RNG | Skips dead agents | Typical use |
|---|---|---:|---:|---|
| `SequentialActivation` | Insertion order | no | yes | deterministic models |
| `RandomActivation` | Random permutation | yes | yes | stochastic activation assumptions |
| `SimultaneousActivation` | all `step()`, then all `advance()` | no | yes | cellular automata and synchronous update models |
| `StagedActivation` | declared stage order | optional | yes | multi-phase agent behaviour |

All built-in schedulers operate on a snapshot of agents selected at the beginning of the scheduler step. Agents created during a scheduler pass are not activated until a later pass.

## SequentialActivation

Activates agents in insertion order.

```python
from abmforge.scheduling import SequentialActivation

self.scheduler = SequentialActivation(self)
```

Use this when deterministic ordering is part of the model design or when you want a simple teaching example.

## RandomActivation

Activates living agents in a deterministic random order using the model-level random number generator.

```python
from abmforge.scheduling import RandomActivation

self.scheduler = RandomActivation(self)
```

Use this when random activation is part of the model assumption.

Given the same model state and seed, `RandomActivation` should produce reproducible activation order.

## SimultaneousActivation

Calls `step()` for all living agents, then calls `advance()` for living agents that define it.

```python
from abmforge.scheduling import SimultaneousActivation

self.scheduler = SimultaneousActivation(self)
```

This is useful when agents should calculate their next state without immediately changing the state observed by other agents.

A typical agent pattern is:

```python
class Cell(Agent):
    def step(self):
        self.next_state = compute_next_state(self)

    def advance(self):
        self.state = self.next_state
```

## StagedActivation

Calls named methods on agents in a specified order.

```python
from abmforge.scheduling import StagedActivation

self.scheduler = StagedActivation(
    self,
    stages=["sense", "decide", "act"],
    shuffle=False,
)
```

If `shuffle=True`, the model-level RNG is used to shuffle agents within each stage.

## Choosing a scheduler

| Modelling need | Recommended scheduler |
|---|---|
| fixed deterministic order | `SequentialActivation` |
| random order each step | `RandomActivation` |
| synchronous update | `SimultaneousActivation` |
| multi-phase agent behaviour | `StagedActivation` |

## Reproducibility notes

For reproducible ABM experiments:

- set the model seed,
- document the scheduler used,
- document whether activation order is deterministic or random,
- avoid relying on accidental dictionary ordering beyond documented insertion-order behaviour,
- include the scheduler choice in scenario or model documentation.

## Common pitfalls

### Activation order affects results

Two models with the same rules but different schedulers may produce different results.

### Newly spawned agents

Built-in schedulers do not activate agents spawned during the same scheduler pass.

### Dead agents

Built-in schedulers skip agents with `is_alive == False`.

### Simultaneous update

With `SimultaneousActivation`, state changes should usually be committed in `advance()`, not directly in `step()`.

## Staged scheduler contract

`StagedActivation` validates its stage list at construction time. The stage list
must be a non-empty sequence of non-empty strings. Passing a single string is
rejected because it would otherwise be interpreted as a sequence of characters.

Each living agent must provide a callable method for each declared stage. If a
stage method is missing or non-callable, ABMForge raises an `AttributeError`
that names the agent type, agent id, and missing stage.

Models may define optional hooks:

```python
def before_stage(self, stage: str) -> None:
    ...

def after_stage(self, stage: str) -> None:
    ...
```

These hooks are called before and after each declared stage. They are useful for
recording stage-level diagnostics, enforcing invariants, or teaching multi-phase
scheduler semantics. Hooks must be callable when defined.

The scheduler still operates on a snapshot of living agents selected at the
beginning of the scheduler step. Agents spawned during a staged scheduler pass
are not activated until a later pass.
