from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from typing import Any


@dataclass(frozen=True, slots=True)
class ExperimentReport:
    """Paths written by the researcher report generator."""

    output_dir: Path
    summary_markdown: Path
    metric_summary_csv: Path
    run_status_csv: Path
    failed_runs_csv: Path


def generate_experiment_report(path: str | Path) -> ExperimentReport:
    """Generate a compact researcher report from experiment output files.

    The current implementation targets the lightweight multi-run output
    directory produced by ``abmforge experiment``.
    """

    output_dir = Path(path)
    reports_dir = output_dir / "reports"
    data_dir = output_dir / "data"

    if not output_dir.exists():
        raise FileNotFoundError(f"Experiment output directory does not exist: {output_dir}")

    summary_path = reports_dir / "experiment_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(
            "Expected experiment summary was not found: "
            f"{summary_path}. Run 'abmforge experiment' first."
        )

    summary = _read_json(summary_path)
    runs = _read_csv(_first_existing(data_dir, ("runs.csv", "run_records.csv")))
    model_records = _read_csv(_first_existing(data_dir, ("model_records.csv", "model.csv")))
    errors = _read_csv(_first_existing(data_dir, ("errors.csv", "error_records.csv")))

    metric_summaries = _summarize_final_model_metrics(model_records)
    run_status_counts = _summarize_run_statuses(runs)
    failed_runs = _find_failed_runs(runs, errors)

    reports_dir.mkdir(parents=True, exist_ok=True)

    metric_summary_csv = reports_dir / "metric_summary.csv"
    run_status_csv = reports_dir / "run_status.csv"
    failed_runs_csv = reports_dir / "failed_runs.csv"
    summary_markdown = reports_dir / "summary.md"

    _write_csv_rows(
        metric_summary_csv,
        metric_summaries,
        default_fields=["metric", "run_count", "mean", "min", "max"],
    )
    _write_counter_csv(run_status_csv, run_status_counts, key_name="status")
    _write_csv_rows(
        failed_runs_csv,
        failed_runs,
        default_fields=["run_id", "status", "error", "exception_type"],
    )
    summary_markdown.write_text(
        _format_summary_markdown(
            summary,
            metric_summaries,
            run_status_counts,
            failed_runs,
        ),
        encoding="utf-8",
    )

    return ExperimentReport(
        output_dir=output_dir,
        summary_markdown=summary_markdown,
        metric_summary_csv=metric_summary_csv,
        run_status_csv=run_status_csv,
        failed_runs_csv=failed_runs_csv,
    )


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")

    return data


def _first_existing(directory: Path, filenames: tuple[str, ...]) -> Path:
    for filename in filenames:
        path = directory / filename
        if path.exists():
            return path

    return directory / filenames[0]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows: list[dict[str, str]] = []

        for row in reader:
            cleaned: dict[str, str] = {}

            for key, value in row.items():
                if key is None:
                    continue

                cleaned[key] = value or ""

            rows.append(cleaned)

        return rows


def _summarize_final_model_metrics(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    latest: dict[tuple[str, str], tuple[int, float]] = {}

    for row in rows:
        run_id = row.get("run_id", "")
        metric = row.get("metric", "") or row.get("name", "")
        step = _safe_int(row.get("step", "")) or 0
        value = _safe_float(row.get("value", ""))

        if not run_id or not metric or value is None:
            continue

        key = (run_id, metric)
        previous = latest.get(key)

        if previous is None or step >= previous[0]:
            latest[key] = (step, value)

    values_by_metric: dict[str, list[float]] = defaultdict(list)

    for (_, metric), (_, value) in latest.items():
        values_by_metric[metric].append(value)

    summaries: list[dict[str, str]] = []

    for metric in sorted(values_by_metric):
        values = values_by_metric[metric]
        summaries.append(
            {
                "metric": metric,
                "run_count": str(len(values)),
                "mean": _format_number(fmean(values)),
                "min": _format_number(min(values)),
                "max": _format_number(max(values)),
            }
        )

    return summaries


def _summarize_run_statuses(rows: list[dict[str, str]]) -> Counter[str]:
    statuses: Counter[str] = Counter()

    for row in rows:
        status = row.get("status", "") or "unknown"
        statuses[status] += 1

    return statuses


def _find_failed_runs(
    runs: list[dict[str, str]],
    errors: list[dict[str, str]],
) -> list[dict[str, str]]:
    failed: list[dict[str, str]] = []

    for row in runs:
        status = row.get("status", "")

        if status and status != "completed":
            failed.append(row)

    if failed or not errors:
        return failed

    for row in errors:
        failed.append(
            {
                "run_id": row.get("run_id", ""),
                "status": "failed",
                "error": row.get("message", "") or row.get("error", ""),
                "exception_type": row.get("exception_type", ""),
            }
        )

    return failed


def _write_counter_csv(path: Path, counter: Counter[str], *, key_name: str) -> None:
    rows = [{key_name: key, "count": str(counter[key])} for key in sorted(counter)]
    _write_csv_rows(path, rows, default_fields=[key_name, "count"])


def _write_csv_rows(
    path: Path,
    rows: list[dict[str, str]],
    *,
    default_fields: list[str],
) -> None:
    fields = list(default_fields)

    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _format_summary_markdown(
    summary: dict[str, Any],
    metrics: list[dict[str, str]],
    statuses: Counter[str],
    failed_runs: list[dict[str, str]],
) -> str:
    name = summary.get("name") or "unnamed"
    model = summary.get("model") or "unknown"
    steps = summary.get("steps", "unknown")
    seed_count = summary.get("seed_count", "unknown")
    expected_runs = summary.get("run_count_expected", "unknown")
    primary_metric = summary.get("primary_metric") or "not specified"

    lines = [
        "# ABMForge experiment report",
        "",
        "## Experiment",
        "",
        f"- Name: `{name}`",
        f"- Model: `{model}`",
        f"- Steps per run: {steps}",
        f"- Seed count: {seed_count}",
        f"- Expected run count: {expected_runs}",
        f"- Primary metric: `{primary_metric}`",
        "",
        "## Run status",
        "",
    ]

    if statuses:
        for status in sorted(statuses):
            lines.append(f"- {status}: {statuses[status]}")
    else:
        lines.append("- No run status records found.")

    lines.extend(["", "## Final model metric summary", ""])

    if metrics:
        lines.extend(
            [
                "| Metric | Runs | Mean | Min | Max |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for row in metrics:
            lines.append("| {metric} | {run_count} | {mean} | {min} | {max} |".format(**row))
    else:
        lines.append("No numeric final model metrics were found.")

    lines.extend(["", "## Failed or non-completed runs", ""])

    if failed_runs:
        lines.append(f"{len(failed_runs)} failed or non-completed run(s) found.")
        lines.append("See `failed_runs.csv` for details.")
    else:
        lines.append("No failed or non-completed runs were found.")

    lines.extend(
        [
            "",
            "## Generated files",
            "",
            "- `summary.md`: this report",
            "- `metric_summary.csv`: numeric final model metric summary",
            "- `run_status.csv`: run status counts",
            "- `failed_runs.csv`: failed or non-completed run details",
            "",
        ]
    )

    return "\n".join(lines)


def _safe_int(value: str) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_number(value: float) -> str:
    return f"{value:.12g}"
