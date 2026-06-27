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
        summarize_metric(model_records, "gini"),
        summarize_metric(model_records, "mean_wealth"),
        summarize_metric(model_records, "max_wealth"),
    ]

    output = archive / "reports" / "wealth_analysis_summary.csv"
    write_summary_csv(rows, output)

    print(f"Wealth analysis summary written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
