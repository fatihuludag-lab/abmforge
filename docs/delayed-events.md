# Delayed Events

ABMForge includes a deterministic event queue for delayed model actions. Each
model owns an `EventQueue` instance at `model.events`.

The event queue is useful when a model needs work to happen at a later model
time without encoding the delay directly inside every agent's `step()` method.

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
