# Agent Lifecycle

ABMForge agents have a small but explicit lifecycle contract.

The goal is to make agent creation, removal, event cancellation, spatial removal, and lifecycle recording predictable and reproducible.

## Lifecycle statuses

ABMForge currently defines two agent lifecycle statuses:

| Status | Meaning |
|---|---|
| `active` | The agent is alive and can participate in simulation |
| `removed` | The agent has been removed from the model |

New agents start as:

```python
agent.lifecycle_status == "active"
agent.is_alive is True
```

When an agent is removed:

```python
agent.lifecycle_status == "removed"
agent.is_alive is False
```

## Creating agents

Agents are normally created through the model's agent collection:

```python
agent = model.agents.create(MyAgent, wealth=10)
```

or in batches:

```python
agents = model.agents.create(MyAgent, n=100, wealth=10)
```

Each agent receives a stable `unique_id`.

## Removing agents

Agents can remove themselves:

```python
agent.remove()
```

This calls:

```python
model.remove_agent(agent)
```

Agents can also be removed directly by id:

```python
model.remove_agent(agent.unique_id)
```

## Removal guarantees

When an agent is removed, ABMForge guarantees the following behaviour:

```text
agent.remove()
  -> agent.is_alive = False
  -> agent.lifecycle_status = "removed"
  -> agent is removed from model.agents
  -> agent is removed from model.world, if a world is attached
  -> pending events owned by the agent are cancelled
  -> lifecycle_records receives an "agent_removed" record
  -> event_records receives "cancelled" records for cancelled owned events
```

This contract makes removal behaviour easier to test, audit, and reproduce.

## Collection removal

After removal, the agent is no longer in the model's agent collection.

```python
agent.remove()

assert agent.unique_id not in model.agents
```

Looking up a removed agent by id should fail.

## World removal

If the model has a spatial world attached, ABMForge attempts to remove the agent from the world as well.

Example:

```python
model.world.place(agent, (2, 2))

agent.remove()

assert not hasattr(agent, "pos")
```

The agent's position is cleared by the space implementation.

## Owned event cancellation

ABMForge's event queue supports event ownership.

When an agent is removed, pending events owned by that agent are cancelled.

Example:

```python
model.events.schedule(
    callback=lambda: None,
    after=1.0,
    owner=agent.unique_id,
)

agent.remove()
```

The pending event is cancelled and should not execute later.

This is important for event-driven ABM models where agents schedule future actions.

## Lifecycle records

Agent removal writes a lifecycle record.

A typical lifecycle record contains:

```text
run_id
step
time
event = "agent_removed"
agent_id
details
```

Lifecycle records make simulation history easier to inspect after a run.

## Event records

If owned events are cancelled during agent removal, ABMForge records event transitions with status:

```text
cancelled
```

This links agent lifecycle changes to the event queue audit trail.

## Snapshot behaviour

`lifecycle_status` is framework-managed lifecycle metadata.

It is intentionally excluded from user-facing agent snapshot state.

For example, if an agent has user attributes:

```python
agent.wealth = 10
agent.mood = "happy"
```

the snapshot user state should contain:

```python
{
    "wealth": 10,
    "mood": "happy",
}
```

not framework internal lifecycle metadata.

## Modelling recommendation

Use `agent.remove()` when the removal is initiated by the agent itself.

Use `model.remove_agent(agent_id)` when the removal is initiated by the model, scheduler, policy rule, or external event.

## Research reproducibility recommendation

If agent removal is part of the model's scientific mechanism, document:

- why agents are removed,
- when removal happens,
- whether removed agents can re-enter,
- whether removal cancels future events,
- which lifecycle records are expected.

This makes model behaviour easier to audit and reproduce.
