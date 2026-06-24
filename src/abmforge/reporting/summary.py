from __future__ import annotations

import ast
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
    parameter_effects_csv: Path
    primary_metric_rankings_csv: Path


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

    latest_metrics = _latest_model_metric_values(model_records)
    metric_summaries = _summarize_final_model_metrics(latest_metrics)
    run_status_counts = _summarize_run_statuses(runs)
    failed_runs = _find_failed_runs(runs, errors)
    run_parameters = _extract_run_parameters(runs)

    primary_metric = summary.get("primary_metric")
    primary_metric_name = primary_metric if isinstance(primary_metric, str) else None
    primary_values = _select_primary_metric_values(latest_metrics, primary_metric_name)

    parameter_effects = _summarize_parameter_effects(primary_values, run_parameters)
    primary_rankings = _summarize_primary_metric_rankings(primary_values, run_parameters)
    key_findings = _build_key_findings(
        summary,
        metric_summaries,
        run_status_counts,
        failed_runs,
        parameter_effects,
        primary_rankings,
    )

    reports_dir.mkdir(parents=True, exist_ok=True)

    metric_summary_csv = reports_dir / "metric_summary.csv"
    run_status_csv = reports_dir / "run_status.csv"
    failed_runs_csv = reports_dir / "failed_runs.csv"
    parameter_effects_csv = reports_dir / "parameter_effects.csv"
    primary_metric_rankings_csv = reports_dir / "primary_metric_rankings.csv"
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
    _write_csv_rows(
        parameter_effects_csv,
        parameter_effects,
        default_fields=[
            "parameter",
            "value",
            "run_count",
            "mean",
            "min",
            "max",
            "difference_from_overall",
        ],
    )
    _write_csv_rows(
        primary_metric_rankings_csv,
        primary_rankings,
        default_fields=[
            "rank_low_to_high",
            "parameter_combination",
            "run_count",
            "mean",
            "min",
            "max",
        ],
    )
    summary_markdown.write_text(
        _format_summary_markdown(
            summary,
            metric_summaries,
            run_status_counts,
            failed_runs,
            parameter_effects,
            primary_rankings,
            key_findings,
        ),
        encoding="utf-8",
    )

    return ExperimentReport(
        output_dir=output_dir,
        summary_markdown=summary_markdown,
        metric_summary_csv=metric_summary_csv,
        run_status_csv=run_status_csv,
        failed_runs_csv=failed_runs_csv,
        parameter_effects_csv=parameter_effects_csv,
        primary_metric_rankings_csv=primary_metric_rankings_csv,
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


def _latest_model_metric_values(
    rows: list[dict[str, str]],
) -> dict[tuple[str, str], float]:
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

    return {key: value for key, (_, value) in latest.items()}


def _summarize_final_model_metrics(
    latest_metrics: dict[tuple[str, str], float],
) -> list[dict[str, str]]:
    values_by_metric: dict[str, list[float]] = defaultdict(list)

    for (_, metric), value in latest_metrics.items():
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


def _extract_run_parameters(
    runs: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    parameters_by_run: dict[str, dict[str, str]] = {}

    for row in runs:
        run_id = row.get("run_id", "")

        if not run_id:
            continue

        parameters: dict[str, str] = {}
        raw_parameters = row.get("parameters", "") or row.get("params", "")
        parsed = _parse_parameter_mapping(raw_parameters)

        for key, value in parsed.items():
            parameters[str(key)] = _stringify_parameter_value(value)

        for key, value in row.items():
            if key in _RUN_METADATA_COLUMNS:
                continue

            if value != "" and key not in parameters:
                parameters[key] = value

        parameters_by_run[run_id] = parameters

    return parameters_by_run


def _parse_parameter_mapping(raw: str) -> dict[str, Any]:
    if not raw:
        return {}

    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(raw)
        except (SyntaxError, ValueError, TypeError, json.JSONDecodeError):
            continue

        if isinstance(parsed, dict):
            return dict(parsed)

    return {}


def _stringify_parameter_value(value: Any) -> str:
    if isinstance(value, str):
        return value

    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _select_primary_metric_values(
    latest_metrics: dict[tuple[str, str], float],
    primary_metric: str | None,
) -> dict[str, float]:
    if primary_metric is None:
        return {}

    return {
        run_id: value
        for (run_id, metric), value in latest_metrics.items()
        if metric == primary_metric
    }


def _summarize_parameter_effects(
    primary_values: dict[str, float],
    run_parameters: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    if not primary_values:
        return []

    overall_mean = fmean(primary_values.values())
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)

    for run_id, value in primary_values.items():
        for parameter, parameter_value in run_parameters.get(run_id, {}).items():
            grouped[(parameter, parameter_value)].append(value)

    rows: list[dict[str, str]] = []

    for (parameter, parameter_value), values in sorted(grouped.items()):
        mean = fmean(values)
        rows.append(
            {
                "parameter": parameter,
                "value": parameter_value,
                "run_count": str(len(values)),
                "mean": _format_number(mean),
                "min": _format_number(min(values)),
                "max": _format_number(max(values)),
                "difference_from_overall": _format_number(mean - overall_mean),
            }
        )

    return rows


def _summarize_primary_metric_rankings(
    primary_values: dict[str, float],
    run_parameters: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    grouped: dict[str, list[float]] = defaultdict(list)

    for run_id, value in primary_values.items():
        parameters = run_parameters.get(run_id, {})
        combination = json.dumps(parameters, sort_keys=True, ensure_ascii=False)
        grouped[combination].append(value)

    ranked = sorted(
        grouped.items(),
        key=lambda item: (fmean(item[1]), item[0]),
    )

    rows: list[dict[str, str]] = []

    for rank, (combination, values) in enumerate(ranked, start=1):
        rows.append(
            {
                "rank_low_to_high": str(rank),
                "parameter_combination": combination,
                "run_count": str(len(values)),
                "mean": _format_number(fmean(values)),
                "min": _format_number(min(values)),
                "max": _format_number(max(values)),
            }
        )

    return rows


def _build_key_findings(
    summary: dict[str, Any],
    metrics: list[dict[str, str]],
    statuses: Counter[str],
    failed_runs: list[dict[str, str]],
    parameter_effects: list[dict[str, str]],
    primary_rankings: list[dict[str, str]],
) -> list[str]:
    findings: list[str] = []
    expected_runs = summary.get("run_count_expected")
    completed_runs = statuses.get("completed", 0)

    if isinstance(expected_runs, int):
        findings.append(f"{completed_runs} of {expected_runs} expected run(s) completed.")
    elif statuses:
        findings.append(f"{completed_runs} completed run(s) were found.")

    if failed_runs:
        findings.append(f"{len(failed_runs)} failed or non-completed run(s) need review.")
    else:
        findings.append("No failed or non-completed runs were found.")

    primary_metric = summary.get("primary_metric")

    if isinstance(primary_metric, str) and primary_rankings:
        lowest = primary_rankings[0]
        highest = primary_rankings[-1]
        findings.append(
            "For primary metric "
            f"`{primary_metric}`, the lowest mean was {lowest['mean']} for "
            f"{lowest['parameter_combination']}."
        )

        if highest is not lowest:
            findings.append(
                f"The highest mean was {highest['mean']} for {highest['parameter_combination']}."
            )

    if parameter_effects:
        strongest = max(
            parameter_effects,
            key=lambda row: abs(_safe_float(row["difference_from_overall"]) or 0.0),
        )
        findings.append(
            "Largest parameter-value deviation from the overall primary-metric mean: "
            f"`{strongest['parameter']}={strongest['value']}` "
            f"({strongest['difference_from_overall']})."
        )
    elif metrics:
        findings.append(
            "No parameter effect table was generated, usually because run "
            "parameters or a primary metric were not available."
        )

    return findings


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
    parameter_effects: list[dict[str, str]],
    primary_rankings: list[dict[str, str]],
    key_findings: list[str],
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
        "## Key findings",
        "",
    ]

    if key_findings:
        for finding in key_findings:
            lines.append(f"- {finding}")
    else:
        lines.append("- No automatic findings were generated.")

    lines.extend(["", "## Run status", ""])

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

    lines.extend(["", "## Primary metric parameter rankings", ""])

    if primary_rankings:
        lines.extend(
            [
                "| Rank low-to-high | Parameter combination | Runs | Mean | Min | Max |",
                "|---:|---|---:|---:|---:|---:|",
            ]
        )
        for row in primary_rankings[:10]:
            lines.append(
                "| {rank_low_to_high} | `{parameter_combination}` | "
                "{run_count} | {mean} | {min} | {max} |".format(**row)
            )
    else:
        lines.append(
            "No primary metric ranking was generated. Check that "
            "`outputs.primary_metric` exists and model records include it."
        )

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
            "- `parameter_effects.csv`: primary metric by parameter value",
            "- `primary_metric_rankings.csv`: parameter combinations ranked low-to-high",
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


_RUN_METADATA_COLUMNS = {
    "run_id",
    "status",
    "seed",
    "steps",
    "name",
    "model",
    "model_name",
    "start_time",
    "end_time",
    "stop_reason",
    "error",
    "exception_type",
    "parameters",
    "params",
}
