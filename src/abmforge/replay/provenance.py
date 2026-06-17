from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(slots=True)
class SnapshotMetadata:
    snapshot_id: str
    created_at: str
    parent_snapshot: str | None
    experiment_id: str | None
    manifest_hash: str | None

    @classmethod
    def create(
        cls,
        *,
        parent_snapshot: str | None = None,
        experiment_id: str | None = None,
        manifest_hash: str | None = None,
    ) -> SnapshotMetadata:
        return cls(
            snapshot_id=f"snapshot-{uuid4().hex}",
            created_at=datetime.now(timezone.utc).isoformat(),
            parent_snapshot=parent_snapshot,
            experiment_id=experiment_id,
            manifest_hash=manifest_hash,
        )
