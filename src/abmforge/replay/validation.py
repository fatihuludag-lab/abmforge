from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from abmforge.replay.snapshot import (
    _normalize_snapshot_value,
    snapshot_hash,
)


@dataclass(slots=True)
class ReplayValidationReport:
    """Report produced by replay snapshot validation."""

    valid: bool
    original_hash: str
    replayed_hash: str
    differences: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return the report as a dictionary."""
        return {
            "valid": self.valid,
            "original_hash": self.original_hash,
            "replayed_hash": self.replayed_hash,
            "differences": list(self.differences),
        }


def validate_replay(
    original_snapshot: dict[str, Any],
    replayed_snapshot: dict[str, Any],
    *,
    include_metadata: bool = False,
) -> ReplayValidationReport:
    """Validate whether two snapshots are replay-equivalent."""
    original_hash = snapshot_hash(
        original_snapshot,
        include_metadata=include_metadata,
    )
    replayed_hash = snapshot_hash(
        replayed_snapshot,
        include_metadata=include_metadata,
    )

    if original_hash == replayed_hash:
        return ReplayValidationReport(
            valid=True,
            original_hash=original_hash,
            replayed_hash=replayed_hash,
            differences=[],
        )

    differences = _diff_values(
        original_snapshot,
        replayed_snapshot,
        include_metadata=include_metadata,
    )

    if not differences:
        differences = ["$: normalized snapshot hashes differ without a structural diff"]

    return ReplayValidationReport(
        valid=False,
        original_hash=original_hash,
        replayed_hash=replayed_hash,
        differences=differences,
    )


def _diff_values(
    left: Any,
    right: Any,
    *,
    path: str = "$",
    include_metadata: bool,
) -> list[str]:
    normalized_left = _normalize_snapshot_value(
        left,
        include_metadata=include_metadata,
    )
    normalized_right = _normalize_snapshot_value(
        right,
        include_metadata=include_metadata,
    )

    return _diff_normalized_values(
        normalized_left,
        normalized_right,
        path=path,
    )


def _diff_normalized_values(left: Any, right: Any, *, path: str) -> list[str]:
    if type(left) is not type(right):
        return [f"{path}: type differs ({type(left).__name__} != {type(right).__name__})"]

    if isinstance(left, dict):
        differences: list[str] = []
        keys = sorted(set(left) | set(right))

        for key in keys:
            next_path = f"{path}.{key}"

            if key not in left:
                differences.append(f"{next_path}: missing from original")
                continue

            if key not in right:
                differences.append(f"{next_path}: missing from replayed")
                continue

            differences.extend(_diff_normalized_values(left[key], right[key], path=next_path))

        return differences

    if isinstance(left, list):
        differences = []

        if len(left) != len(right):
            differences.append(f"{path}: length differs ({len(left)} != {len(right)})")

        for index, (left_item, right_item) in enumerate(zip(left, right, strict=False)):
            differences.extend(
                _diff_normalized_values(
                    left_item,
                    right_item,
                    path=f"{path}[{index}]",
                )
            )

        return differences

    if left != right:
        return [f"{path}: value differs ({left!r} != {right!r})"]

    return []
