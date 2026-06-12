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
