from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_reproducible_study_example_creates_valid_archive(tmp_path: Path) -> None:
    script = ROOT / "examples" / "reproducible_study" / "reproduce.py"
    archive = tmp_path / "reproducible_study_archive"

    subprocess.run(
        [
            sys.executable,
            str(script),
            "--output",
            str(archive),
        ],
        cwd=ROOT,
        check=True,
    )

    assert (archive / "manifest.json").exists()
    assert (archive / "dataset_schema.json").exists()
    assert (archive / "run_index.json").exists()
    assert (archive / "configs" / "experiment.yaml").exists()
    assert (archive / "data" / "runs.json").exists()
    assert (archive / "data" / "runs.csv").exists()
    assert (archive / "data" / "model_records.csv").exists()
    assert (archive / "reports" / "experiment_summary.json").exists()
    assert (archive / "reports" / "summary.md").exists()
    assert (archive / "reports" / "reproducible_study_summary.csv").exists()
    assert (archive / "reports" / "reproducible_study_adoption_curve.csv").exists()
    assert (archive / "reports" / "reproducible_study_adoption_curve.svg").exists()
