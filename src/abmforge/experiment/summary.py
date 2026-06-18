from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from abmforge.experiment.archive import ExperimentArchive

_DATASET_JSON_FILES = {
    "runs": "runs.json",
    "model_records": "model_records.jsonl",
    "agent_records": "agent_records.jsonl",
    "event_records": "event_records.jsonl",
    "lifecycle_records": "lifecycle_records.jsonl",
    "errors": "errors.jsonl",
}


def _read_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        return {}

    return data


def _count_json_array(path: Path) -> int | None:
    if not path.is_file():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        return None

    return len(data)


def _count_jsonl(path: Path) -> int | None:
    if not path.is_file():
        return None

    count = 0

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1

    return count


def _count_json_records(data_dir: Path) -> dict[str, int | None]:
    counts: dict[str, int | None] = {}

    for table_name, filename in _DATASET_JSON_FILES.items():
        path = data_dir / filename

        if filename.endswith(".jsonl"):
            counts[table_name] = _count_jsonl(path)
        else:
            counts[table_name] = _count_json_array(path)

    return counts


def summarize_archive(path: str | Path) -> dict[str, Any]:
    """Return a compact summary of an ABMForge experiment archive."""
    archive = ExperimentArchive(Path(path))
    validation_errors = archive.validate()

    manifest = _read_json_object(archive.manifest_path)
    run_summary = _read_json_object(archive.reports_dir / "run_summary.json")

    manifest_counts = manifest.get("record_counts", {})
    if not isinstance(manifest_counts, dict):
        manifest_counts = {}

    summary = {
        "archive_path": str(archive.path),
        "valid": not validation_errors,
        "validation_errors": validation_errors,
        "run_id": manifest.get("run_id") or run_summary.get("run_id"),
        "status": manifest.get("status") or run_summary.get("status"),
        "scenario": manifest.get("scenario"),
        "model_name": manifest.get("model_name"),
        "seed": manifest.get("seed"),
        "abmforge_version": manifest.get("abmforge_version"),
        "dataset_schema_version": manifest.get("dataset_schema_version"),
        "manifest_id": manifest.get("manifest_id"),
        "record_counts": {
            "manifest": manifest_counts,
            "files": _count_json_records(archive.data_dir),
        },
    }

    return summary


def format_archive_summary(summary: dict[str, Any]) -> str:
    """Format an archive summary for CLI output."""
    lines = [
        "ABMForge archive summary",
        f"Archive: {summary['archive_path']}",
        f"Valid: {'yes' if summary['valid'] else 'no'}",
    ]

    if summary["validation_errors"]:
        lines.append("")
        lines.append("Validation errors:")

        for error in summary["validation_errors"]:
            lines.append(f"- {error}")

    lines.extend(
        [
            "",
            "Run metadata:",
            f"- run_id: {summary.get('run_id')}",
            f"- status: {summary.get('status')}",
            f"- scenario: {summary.get('scenario')}",
            f"- model_name: {summary.get('model_name')}",
            f"- seed: {summary.get('seed')}",
            f"- abmforge_version: {summary.get('abmforge_version')}",
            f"- dataset_schema_version: {summary.get('dataset_schema_version')}",
            f"- manifest_id: {summary.get('manifest_id')}",
            "",
            "Record counts:",
        ]
    )

    manifest_counts = summary["record_counts"]["manifest"]
    file_counts = summary["record_counts"]["files"]

    table_names = sorted(set(manifest_counts) | set(file_counts))

    for table_name in table_names:
        manifest_count = manifest_counts.get(table_name)
        file_count = file_counts.get(table_name)
        lines.append(f"- {table_name}: manifest={manifest_count}, files={file_count}")

    return "\n".join(lines)
