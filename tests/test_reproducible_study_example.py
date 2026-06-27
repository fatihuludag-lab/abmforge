from __future__ import annotations

import json
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

    expected_files = [
        "manifest.json",
        "dataset_schema.json",
        "run_index.json",
        "configs/experiment.yaml",
        "data/runs.json",
        "data/runs.csv",
        "data/model_records.csv",
        "reports/experiment_summary.json",
        "reports/summary.md",
        "reports/reproducible_study_summary.csv",
        "reports/reproducible_study_adoption_curve.csv",
        "reports/reproducible_study_adoption_curve.svg",
        "reports/ODD.md",
        "reports/ODD.json",
        "reports/research_protocol.md",
        "reports/artifact_manifest.json",
    ]

    for relative_path in expected_files:
        assert (archive / relative_path).exists(), relative_path

    odd_payload = json.loads((archive / "reports" / "ODD.json").read_text(encoding="utf-8"))
    assert odd_payload["model"]["name"] == "ThresholdAdoptionModel"
    assert odd_payload["manual_review_required"] is True
    assert odd_payload["completeness"]["entities"] is True
    assert odd_payload["completeness"]["process_overview"] is True

    artifact_manifest = json.loads(
        (archive / "reports" / "artifact_manifest.json").read_text(encoding="utf-8")
    )
    assert artifact_manifest["schema_version"] == "abmforge.example_artifacts.v1"
    assert all(item["exists"] for item in artifact_manifest["artifacts"])
