# Scheduling

> **Normative semantics:** This page explains how to use the available
> schedulers. The authoritative description of activation order, agent
> eligibility, lifecycle visibility, random-stream limitations, and current
> versus target guarantees is
> [Simulation Semantics V1](simulation-semantics-v1.md).

Scheduling controls the order in which agents act.

Activation order is a modelling assumption. In agent-based modelling, changing the scheduler can change the simulation result. ABMForge therefore treats schedulers as explicit model components.

## Built-in schedulers

| Scheduler | Activation order | Uses scheduler RNG | Skips dead agents | Typical use |
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

Activates living agents in a deterministic random order using the named `scheduler` random stream obtained from `model.rng_stream("scheduler")`.

```python
from abmforge.scheduling import RandomActivation

self.scheduler = RandomActivation(self)
```

Use this when random activation is part of the model assumption.

Given the same candidate history, model seed, and scheduler-stream draw history, `RandomActivation` produces reproducible activation order. The default `model.rng` stream remains available to model and agent behavior, so unrelated behavior draws do not change later activation order.

## SimultaneousActivation

Calls `step()` for every eligible agent, then calls `advance()` for every
agent that remains eligible.

Before any callback runs, the scheduler validates the initial eligible
candidate snapshot. Every participating agent must define callable `step()`
and `advance()` methods.

If one or more candidates violate this contract, ABMForge raises one
`TypeError` that identifies every invalid agent and each missing or
non-callable method. No activation callback is executed.

```python
from abmforge.scheduling import SimultaneousActivation

self.scheduler = SimultaneousActivation(self)
```

This scheduler is useful when agents should calculate pending state without
immediately changing the state observed by other agents.

A typical agent pattern is:

```python
class Cell(Agent):
    def step(self):
        self.next_state = compute_next_state(self)

    def advance(self):
        self.state = self.next_state
```

An agent that intentionally has no commit work must still define a callable
no-op `advance()` method:

```python
def advance(self) -> None:
    pass
```

Agents that are already ineligible when the scheduler call begins are excluded
from strict two-phase capability validation.

The scheduler guarantees phase ordering, but it does not automatically isolate
current and next state. Model authors must avoid directly mutating current
state in `step()` when later decision callbacks must observe the old state.

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

If `shuffle=True`, the named `scheduler` random stream is used to shuffle agents within each stage.

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

With `SimultaneousActivation`, decision calculations belong in `step()` and pending-state commits belong in `advance()`. The scheduler enforces the two callable methods and their phase order, but it cannot prevent a model implementation from mutating current state directly in `step()`.

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

## Random-stream separation

Randomized built-in activation paths use the named `scheduler` random stream:

- `RandomActivation`;
- `AgentCollection.shuffle_do()`;
- shuffled `StagedActivation`.

They obtain this generator through `model.rng_stream("scheduler")`.

The default `model.rng` stream remains available for ordinary model and agent
behavior. Consuming that default stream does not consume the scheduler stream,
so unrelated behavior draws do not change later activation order.

Named streams are cached by name and derived independently of stream creation
order. Custom model components can request their own stream with
`model.rng_stream("component-name")`.

## Scheduler metadata

Schedulers expose `to_metadata()` for JSON-serializable audit metadata. The base
scheduler metadata uses schema version `scheduler-metadata-v1` and includes:

- `schema_version`;
- `scheduler_type`;
- `module`;
- `attached`.

`StagedActivation.to_metadata()` also records:

- `stages`;
- `shuffle`.

This metadata is intended for inspection and snapshot audit trails. It is not a scheduler restore contract.

## Activation Eligibility

All built-in schedulers use callback-time activation eligibility validation.

A candidate agent receives a callback only when:

- the agent is still present in the model collection;
- the collection still stores the same object under that identifier;
- the candidate remains alive.

Built-in schedulers create a candidate snapshot when the scheduler call begins.
As a result:

- agents added during the call are deferred until the next scheduler call;
- agents removed before their turn are skipped;
- agents marked not alive before their turn are skipped;
- replacing an agent with a new object using the same identifier does not
  activate either object from the stale snapshot position.

`SimultaneousActivation` first validates the complete initially eligible
candidate snapshot for callable `step()` and `advance()` methods. This
preflight validation finishes before any callback is invoked. It then applies
the eligibility check independently before every decision and commit callback.

`StagedActivation` applies the eligibility check before every stage callback.

Custom schedulers should follow the same contract unless they explicitly
declare and document a different experimental execution profile.
