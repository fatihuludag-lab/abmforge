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

## Snapshot serialization and restore invariants

Snapshot files use a fail-closed JSON contract.

`write_snapshot(...)` and `snapshot_hash(...)` accept only values that can be
represented faithfully as standard JSON. Unsupported Python objects, sets,
non-finite numbers, and similar values raise an error instead of being silently
converted to strings.

```python
snapshot = model.snapshot()
write_snapshot(snapshot, "outputs/snapshot.json")
```

A failed serialization does not create the requested output file.

`read_snapshot(...)` requires the top-level JSON value to be an object. Arrays,
strings, numbers, booleans, and `null` are rejected as snapshot documents.

### Restore validation

`Model.from_snapshot(...)` validates framework-managed state before restoring
the model.

The following guarantees apply:

- `schema_version` must be supported;
- `run_id` must be a string;
- `step` must be a non-negative integer and cannot be a boolean;
- `time` must be a finite, non-negative number and cannot be a boolean;
- `parameters`, `model_state`, RNG state, agent records, and agent state must
  use the expected container types;
- simultaneous `id` and `agent_id` values must match;
- duplicate agent identifiers are rejected by the agent collection;
- unknown custom agent classes require an explicit `agent_classes` mapping.

### Protected model state

User `model_state` cannot overwrite framework-managed attributes such as:

```text
parameters
seed
rng
run_id
steps
time
running
status
agents
events
record
world
scheduler
schedule
```

Private model fields whose names begin with `_` are also rejected during
restore.

### Protected agent state

Agent user state cannot overwrite framework-managed attributes such as:

```text
model
unique_id
is_alive
lifecycle_status
world
pos
```

Private agent fields whose names begin with `_` are also rejected.

Spatial references are not stored as ordinary agent state. When available,
agent position is represented separately by the snapshot `position` field.
World, scheduler, and event-queue metadata remain audit information and are not
restored as live framework objects.

## Replay validation

Use `validate_replay(...)` to compare an original snapshot with a replayed or
restored snapshot:

```python
from abmforge import validate_replay

report = validate_replay(
    original_snapshot,
    replayed_snapshot,
)

assert report.valid
```

`ReplayValidationReport` contains:

- `valid`;
- `original_hash`;
- `replayed_hash`;
- `differences`.

Snapshot hashing and structural difference analysis use the same canonical
normalization. Therefore, a replay report cannot normally claim that hashes
differ while returning an empty difference list.

Every report with `valid=False` contains at least one machine-readable
difference message. Difference paths use a root-based notation such as:

```text
$.model_state.population
$.agents[0].state.wealth
$.scheduler.type
```

### Metadata handling

By default, `validate_replay(...)` uses `include_metadata=False`.

Framework-managed provenance and structural type metadata are ignored,
including:

- top-level model and snapshot provenance fields;
- snapshot identifiers and creation timestamps;
- agent class metadata;
- scheduler and similar structural `type` metadata.

User-controlled values remain part of replay validation. A user parameter,
model-state field, or agent-state field named `type` is not discarded.

To compare framework metadata as well as scientific state:

```python
report = validate_replay(
    original_snapshot,
    replayed_snapshot,
    include_metadata=True,
)
```

With metadata enabled, differences such as `$.scheduler.type` are reported.

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

This metadata is intended for audit, inspection, and debugging. This metadata is not a full event replay contract. Callback functions are
not serialized and
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
