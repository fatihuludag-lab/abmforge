from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


def analyze_archive(archive_path: str | Path) -> dict[str, object]:
    """Create lightweight analysis artifacts from an ABMForge experiment archive."""

    archive = Path(archive_path)
    model_records_path = archive / "data" / "model_records.csv"
    run_records_path = archive / "data" / "runs.csv"

    if not model_records_path.exists():
        raise FileNotFoundError(f"Missing model records table: {model_records_path}")

    records = _read_csv(model_records_path)
    runs = _read_csv(run_records_path) if run_records_path.exists() else []

    final_adoption = _final_metric_by_run(records, "adoption_share")
    mean_curve = _mean_metric_by_step(records, "adoption_share")
    new_adoption_curve = _mean_metric_by_step(records, "new_adoptions")

    report_dir = archive / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    summary_csv = report_dir / "reproducible_study_summary.csv"
    _write_summary_csv(summary_csv, final_adoption)

    curve_csv = report_dir / "reproducible_study_adoption_curve.csv"
    _write_curve_csv(curve_csv, mean_curve, new_adoption_curve)

    summary_json = report_dir / "reproducible_study_summary.json"
    summary = {
        "run_count": len(final_adoption),
        "run_records": len(runs),
        "mean_final_adoption_share": _mean(list(final_adoption.values())),
        "min_final_adoption_share": min(final_adoption.values()) if final_adoption else None,
        "max_final_adoption_share": max(final_adoption.values()) if final_adoption else None,
        "summary_csv": str(summary_csv.relative_to(archive)),
        "curve_csv": str(curve_csv.relative_to(archive)),
        "curve_svg": "reports/reproducible_study_adoption_curve.svg",
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    svg_path = report_dir / "reproducible_study_adoption_curve.svg"
    _write_svg_line_chart(svg_path, mean_curve, title="Mean adoption share by step")

    return summary


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _final_metric_by_run(records: list[dict[str, str]], metric: str) -> dict[str, float]:
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in records:
        if row.get("metric") != metric:
            continue
        run_id = row["run_id"]
        step = float(row.get("step") or 0.0)
        value = float(row["value"])
        grouped[run_id].append((step, value))

    final: dict[str, float] = {}
    for run_id, values in grouped.items():
        values.sort(key=lambda item: item[0])
        final[run_id] = values[-1][1]
    return final


def _mean_metric_by_step(records: list[dict[str, str]], metric: str) -> dict[int, float]:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in records:
        if row.get("metric") != metric:
            continue
        step = int(float(row.get("step") or 0.0))
        grouped[step].append(float(row["value"]))
    return {step: _mean(values) for step, values in sorted(grouped.items())}


def _write_summary_csv(path: Path, final_adoption: dict[str, float]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["run_id", "final_adoption_share"])
        writer.writeheader()
        for run_id, value in sorted(final_adoption.items()):
            writer.writerow({"run_id": run_id, "final_adoption_share": value})


def _write_curve_csv(
    path: Path,
    adoption_curve: dict[int, float],
    new_adoption_curve: dict[int, float],
) -> None:
    steps = sorted(set(adoption_curve) | set(new_adoption_curve))
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "step",
                "mean_adoption_share",
                "mean_new_adoptions",
            ],
        )
        writer.writeheader()
        for step in steps:
            writer.writerow(
                {
                    "step": step,
                    "mean_adoption_share": adoption_curve.get(step, 0.0),
                    "mean_new_adoptions": new_adoption_curve.get(step, 0.0),
                }
            )


def _write_svg_line_chart(path: Path, curve: dict[int, float], *, title: str) -> None:
    width = 720
    height = 420
    margin = 48
    plot_width = width - 2 * margin
    plot_height = height - 2 * margin

    points = []
    if curve:
        min_step = min(curve)
        max_step = max(curve)
        step_span = max(1, max_step - min_step)

        for step, value in sorted(curve.items()):
            x = margin + ((step - min_step) / step_span) * plot_width
            y = margin + (1.0 - max(0.0, min(1.0, value))) * plot_height
            points.append(f"{x:.1f},{y:.1f}")

    polyline = " ".join(points)
    svg_lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        f"  <title>{title}</title>",
        '  <rect width="100%" height="100%" fill="white"/>',
        (
            f'  <line x1="{margin}" y1="{height - margin}" '
            f'x2="{width - margin}" y2="{height - margin}" stroke="black"/>'
        ),
        (
            f'  <line x1="{margin}" y1="{margin}" '
            f'x2="{margin}" y2="{height - margin}" stroke="black"/>'
        ),
        (
            f'  <text x="{width / 2}" y="28" text-anchor="middle" '
            f'font-family="sans-serif" font-size="18">{title}</text>'
        ),
        (
            f'  <text x="{width / 2}" y="{height - 10}" text-anchor="middle" '
            'font-family="sans-serif" font-size="13">Simulation step</text>'
        ),
        (
            f'  <text x="16" y="{height / 2}" '
            f'transform="rotate(-90 16 {height / 2})" '
            'text-anchor="middle" font-family="sans-serif" '
            'font-size="13">Adoption share</text>'
        ),
        (f'  <polyline fill="none" stroke="black" stroke-width="2.5" points="{polyline}"/>'),
        "</svg>",
        "",
    ]
    path.write_text("\n".join(svg_lines), encoding="utf-8")


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("archive", help="Path to an ABMForge experiment archive")
    args = parser.parse_args()

    result = analyze_archive(args.archive)
    print(json.dumps(result, indent=2))
