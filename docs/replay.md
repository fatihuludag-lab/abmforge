# Replay and Snapshots

ABMForge provides simple snapshot read/write helpers.

## Write a Snapshot

```python
from abmforge import write_snapshot

snapshot = model.snapshot()
write_snapshot(snapshot, "outputs/snapshot.json")
```

## Read a Snapshot

```python
from abmforge import read_snapshot

snapshot = read_snapshot("outputs/snapshot.json")
```

## Current Scope

The current snapshot system stores JSON-serializable model state.

Future versions may support:

- full replay
- event trace replay
- deterministic debugging
- snapshot comparison
- checkpointing

## Event queue metadata

Model snapshots include an `event_queue` metadata block. This block records
pending event ids, times, priorities, sequence numbers, owners, tags,
cancellation flags, and callback module/name metadata.

Example shape:

```json
{
  "schema_version": "event-queue-metadata-v1",
  "pending_count": 1,
  "cancelled_count": 0,
  "next_event_time": 3.0,
  "callback_restore_supported": false,
  "events": [
    {
      "event_id": 1,
      "time": 3.0,
      "priority": 0,
      "sequence": 1,
      "owner": "agent-1",
      "tags": ["demo"],
      "cancel_on_owner_removed": true,
      "cancelled": false,
      "callback": {
        "module": "example",
        "qualname": "callback"
      }
    }
  ]
}
```

This metadata is intended for audit, inspection, and debugging. This metadata is not a full event replay contract.
event replay contract. Callback functions are not serialized and
`Model.from_snapshot(...)` does not restore queued callbacks.

Use `model.events.snapshot_metadata(include_cancelled=True)` when cancelled
events should be included in the audit view.

## Scheduler metadata

Model snapshots include a `scheduler` metadata block. When a model has no
attached scheduler, the block records:

```json
{
  "schema_version": "scheduler-metadata-v1",
  "attached": false
}
```

When a scheduler object is attached to the model through `_scheduler`,
`scheduler`, or `schedule`, ABMForge records its scheduler type, module, and
available scheduler-specific metadata. For example, `StagedActivation` records
its stage list and shuffle setting.

This metadata is not a scheduler restore contract. `Model.from_snapshot(...)`
does not reconstruct scheduler instances from snapshot metadata.
