from __future__ import annotations

import sys
from pathlib import Path

from abmforge.analysis import summarize_metric, write_summary_csv
from abmforge.analysis.archive_tables import load_archive_table


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args:
        print("Usage: python analysis/analyze.py <archive>")
        return 2

    archive = Path(args[0])
    model_records = load_archive_table(archive, "model_records")

    rows = [
        summarize_metric(model_records, "adoption_share"),
        summarize_metric(model_records, "adopter_count"),
        summarize_metric(model_records, "new_adoptions"),
    ]

    output = archive / "reports" / "diffusion_analysis_summary.csv"
    write_summary_csv(rows, output)

    print(f"Diffusion analysis summary written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
