from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias

from .archive_tables import load_archive_tables

Record: TypeAlias = Mapping[str, Any]
SummaryRow: TypeAlias = dict[str, Any]


class RobustnessSummaryError(ValueError):
    """Raised when a robustness summary cannot be computed."""


def summarize_metric(
    records: Iterable[Record],
    metric: str,
    *,
    metric_field: str = "metric",
    value_field: str = "value",
    run_id_field: str = "run_id",
    step_field: str = "step",
    latest_per_run: bool = True,
) -> SummaryRow:
    """Summarize one metric across records.

    By default, the function selects the latest record per run before computing
    summary statistics. This is usually what researchers want for final-output
    ABM metrics recorded over time.
    """
    selected = _select_metric_records(
        records,
        metric,
        metric_field=metric_field,
        value_field=value_field,
        run_id_field=run_id_field,
        step_field=step_field,
        latest_per_run=latest_per_run,
    )
    values = [_to_float(record[value_field]) for record in selected]

    return _numeric_summary(metric=metric, values=values)


def summarize_metric_by_parameters(
    archive: str | Path,
    metric: str,
    group_by: Sequence[str],
    *,
    metric_field: str = "metric",
    value_field: str = "value",
    run_id_field: str = "run_id",
    step_field: str = "step",
    latest_per_run: bool = True,
) -> list[SummaryRow]:
    """Summarize a metric grouped by run parameters.

    The function loads ``runs`` and ``model_records`` from an ABMForge archive.
    It supports run parameters stored as nested dictionaries, JSON strings, or
    direct columns on the ``runs`` table.
    """
    if not group_by:
        raise RobustnessSummaryError("group_by must contain at least one field")

    tables = load_archive_tables(
        archive,
        tables=["runs", "model_records"],
        missing="raise",
    )
    runs = _ensure_records(tables["runs"], table="runs")
    model_records = _ensure_records(tables["model_records"], table="model_records")

    selected = _select_metric_records(
        model_records,
        metric,
        metric_field=metric_field,
        value_field=value_field,
        run_id_field=run_id_field,
        step_field=step_field,
        latest_per_run=latest_per_run,
    )
    run_context = _run_context_by_id(runs, run_id_field=run_id_field)

    grouped: dict[tuple[Any, ...], list[float]] = defaultdict(list)

    for record in selected:
        run_id = record.get(run_id_field)
        context = run_context.get(str(run_id), {})
        key = tuple(_lookup_group_value(context, field) for field in group_by)
        grouped[key].append(_to_float(record[value_field]))

    rows: list[SummaryRow] = []

    for key in sorted(grouped, key=lambda item: tuple(str(part) for part in item)):
        values = grouped[key]
        row = _numeric_summary(metric=metric, values=values)
        for field, value in zip(group_by, key, strict=True):
            row[field] = value
        rows.append(row)

    return rows


def write_summary_csv(rows: SummaryRow | Sequence[SummaryRow], output: str | Path) -> Path:
    """Write a robustness summary dictionary or row list to CSV."""
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    row_list = [rows] if isinstance(rows, dict) else list(rows)
    fieldnames = _fieldnames(row_list)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(row_list)

    return output_path


def _select_metric_records(
    records: Iterable[Record],
    metric: str,
    *,
    metric_field: str,
    value_field: str,
    run_id_field: str,
    step_field: str,
    latest_per_run: bool,
) -> list[Record]:
    metric_records = [
        record
        for record in records
        if record.get(metric_field) == metric and record.get(value_field) is not None
    ]

    if not metric_records:
        raise RobustnessSummaryError(f"No records found for metric: {metric}")

    if not latest_per_run:
        return metric_records

    latest: dict[str, Record] = {}

    for record in metric_records:
        run_id = str(record.get(run_id_field, "__single_run__"))
        previous = latest.get(run_id)
        if previous is None or _step_value(record, step_field) >= _step_value(
            previous,
            step_field,
        ):
            latest[run_id] = record

    return list(latest.values())


def _numeric_summary(*, metric: str, values: Sequence[float]) -> SummaryRow:
    if not values:
        raise RobustnessSummaryError(f"No numeric values available for metric: {metric}")

    count = len(values)
    mean = statistics.fmean(values)
    std = statistics.stdev(values) if count > 1 else 0.0

    return {
        "metric": metric,
        "count": count,
        "mean": mean,
        "std": std,
        "min": min(values),
        "max": max(values),
    }


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RobustnessSummaryError(f"Metric value is not numeric: {value!r}") from exc


def _step_value(record: Record, step_field: str) -> int:
    value = record.get(step_field, 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _ensure_records(value: Any, *, table: str) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, Mapping)]
    raise RobustnessSummaryError(f"Expected table '{table}' to load as list[dict]")


def _run_context_by_id(
    runs: Iterable[Record],
    *,
    run_id_field: str,
) -> dict[str, dict[str, Any]]:
    contexts: dict[str, dict[str, Any]] = {}

    for index, run in enumerate(runs):
        run_id = str(run.get(run_id_field, index))
        context = dict(run)

        for key in ("parameters", "params", "base_parameters"):
            nested = _parse_maybe_json_mapping(run.get(key))
            if nested:
                context.update({str(name): value for name, value in nested.items()})

        contexts[run_id] = context

    return contexts


def _parse_maybe_json_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return {}
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, Mapping):
            return dict(parsed)

    return {}


def _lookup_group_value(context: Mapping[str, Any], field: str) -> Any:
    if field in context:
        return context[field]

    candidates = (
        f"parameter_{field}",
        f"parameters.{field}",
        f"params.{field}",
        f"base_parameters.{field}",
    )
    for candidate in candidates:
        if candidate in context:
            return context[candidate]

    return None


def _fieldnames(rows: Sequence[SummaryRow]) -> list[str]:
    preferred = ["metric", "count", "mean", "std", "min", "max"]
    discovered: list[str] = []

    for row in rows:
        for key in row:
            if key not in discovered:
                discovered.append(key)

    return [key for key in preferred if key in discovered] + [
        key for key in discovered if key not in preferred
    ]
