from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


def read_json_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def latest_metric(records: list[dict[str, Any]], metric: str) -> float | None:
    values = [
        item for item in records if item.get("metric") == metric and item.get("value") is not None
    ]
    if not values:
        return None
    values.sort(key=lambda item: (str(item.get("run_id", "")), int(item.get("step", 0))))
    return float(values[-1]["value"])


def write_summary(archive: Path) -> Path:
    data_dir = archive / "data"
    reports_dir = archive / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    model_records = read_json_records(data_dir / "model_records.json")
    runs = read_json_records(data_dir / "runs.json")

    output = reports_dir / "analysis_summary.csv"

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerow({"metric": "run_count", "value": len(runs)})
        writer.writerow(
            {
                "metric": "latest_adoption_share",
                "value": latest_metric(model_records, "adoption_share"),
            }
        )
        writer.writerow(
            {
                "metric": "latest_adopter_count",
                "value": latest_metric(model_records, "adopter_count"),
            }
        )
        writer.writerow(
            {
                "metric": "latest_mean_threshold",
                "value": latest_metric(model_records, "mean_threshold"),
            }
        )

    return output


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args:
        print("Usage: python analysis/analyze.py <archive>")
        return 2

    archive = Path(args[0])
    if not archive.exists():
        print(f"Archive does not exist: {archive}")
        return 1

    output = write_summary(archive)
    print(f"Analysis summary written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
