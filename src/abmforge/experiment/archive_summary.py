from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from abmforge.experiment.archive_loader import load_archive_run_records


def summarize_archive_runs(path: str | Path) -> dict[str, Any]:
    """Summarize archive-level run metadata.

    The summary is intentionally small and dependency-free. It is designed for
    quick inspection of archived runs before loading larger dataset tables.
    """
    return summarize_run_records(load_archive_run_records(path))


def summarize_run_records(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize run metadata records."""
    materialized = [dict(record) for record in records]

    status_counts = _count_by(materialized, "status")
    scenario_counts = _count_by(materialized, "scenario")
    model_counts = _count_by(materialized, "model_name")

    return {
        "run_count": len(materialized),
        "completed_count": status_counts.get("completed", 0),
        "failed_count": status_counts.get("failed", 0),
        "status_counts": status_counts,
        "scenario_counts": scenario_counts,
        "model_counts": model_counts,
        "seed_count": _unique_count(materialized, "seed"),
        "step_summary": _numeric_summary(materialized, "steps"),
    }


def _count_by(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter: Counter[str] = Counter()

    for record in records:
        value = record.get(key)
        if value is not None:
            counter[str(value)] += 1

    return dict(sorted(counter.items()))


def _unique_count(records: list[dict[str, Any]], key: str) -> int:
    values = {record.get(key) for record in records if record.get(key) is not None}
    return len(values)


def _numeric_summary(records: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = [_as_float(record.get(key)) for record in records]
    numeric_values = [value for value in values if value is not None]

    if not numeric_values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
        }

    return {
        "count": len(numeric_values),
        "min": min(numeric_values),
        "max": max(numeric_values),
        "mean": sum(numeric_values) / len(numeric_values),
    }


def _as_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, int | float):
        return float(value)

    try:
        return float(value)
    except (TypeError, ValueError):
        return None
