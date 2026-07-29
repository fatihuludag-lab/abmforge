# Delayed Events

> **Normative semantics:** This page documents the event-queue API. The
> authoritative description of fixed-step integer ticks, event phases,
> same-tick scheduling, and current event-time guarantees is
> [Simulation Semantics V1](simulation-semantics-v1.md).

ABMForge includes a deterministic event queue for delayed model actions. Each
model owns an `EventQueue` instance at `model.events`.

The event queue is useful when a model needs work to happen at a later model
time without encoding the delay directly inside every agent's `step()` method.

## Fixed-Step Integer-Tick Contract

The built-in model runner advances simulation time in steps of `1.0`.
Delayed events therefore use non-negative integer-valued simulation ticks.

Accepted examples:

```python
model.events.schedule_at(3, callback=callback)
model.events.schedule_at(3.0, callback=callback)
model.events.schedule_after(2, callback=callback)
model.events.schedule_after(2.0, callback=callback)
```

Integer-valued floats such as `1.0` are accepted and normalized to
`float`.

Rejected examples:

```python
model.events.schedule_at(0.5, callback=callback)
model.events.schedule_after(1.25, callback=callback)
model.events.schedule_at(True, callback=callback)
model.events.schedule_after("2", callback=callback)
```

The fixed-step contract rejects:

- fractional absolute event times;
- fractional delays;
- Boolean values;
- strings and objects accepted only through implicit numeric coercion;
- non-finite values;
- negative delays;
- absolute times earlier than the current model time.

A rejected scheduling request does not:

- consume an event identifier;
- create a pending event;
- write an event record.

The built-in fixed-step event queue is not a continuous-time or general
discrete-event simulation engine.

## Scheduling events

Use `schedule_after(...)` for relative delays:

```python
model.events.schedule_after(
    2,
    callback=lambda: print("runs two model-time units later"),
    tags=["demo"],
)
```

Use `schedule_at(...)` for absolute model time:

```python
model.events.schedule_at(
    10,
    callback=lambda: print("runs at model time 10"),
    owner="agent-1",
)
```

The lower-level `schedule(...)` method remains available and accepts exactly one
of `at=` or `after=`.

```python
model.events.schedule(callback=callback, after=1)
model.events.schedule(callback=callback, at=5)
```

## Inspection helpers

The queue exposes small read-only inspection helpers:

```python
model.events.pending_events()
model.events.pending_events(owner="agent-1")
model.events.pending_events(tag="infection")
model.events.next_event_time()
model.events.has_pending()
model.events.pending_count()
```

`pending_events(...)` returns events in deterministic execution order, sorted by
time, priority, sequence, and event id.

## Cancellation

Events can be cancelled by event id, owner, or tag:

```python
event = model.events.schedule_after(1, callback=callback, owner="agent-1")
model.events.cancel(event.event_id)
model.events.cancel_by_owner("agent-1")
model.events.cancel_by_tag("infection")
```

When an agent is removed through `Model.remove_agent(...)`, events owned by that
agent are cancelled automatically when `cancel_on_owner_removed=True`.

## Execution order

`Model.run_for(...)` processes due events before the model's `step()` method for
the current model time. This means events scheduled for the current time are
executed before the next model step body.

## Current limitation

Event queue inspection is not full event replay. Callback functions are not
serialized into snapshots, and event queue state is not yet restored by
`Model.from_snapshot(...)`. Treat the event queue as a delayed-action mechanism
and audit trail, not a full deterministic replay system.
