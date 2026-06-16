from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model_zoo.schelling.model import SchellingModel
from model_zoo.schelling.run import build_odd_document as build_schelling_odd
from model_zoo.sir.model import SIRModel
from model_zoo.sir.run import build_odd_document as build_sir_odd

from abmforge import ReproducibilityManifest, Scenario

ROOT = Path(__file__).resolve().parents[1]


def test_schelling_model_zoo_dataset_validates() -> None:
    result = Scenario(
        model=SchellingModel,
        seed=42,
        steps=3,
        name="test-schelling",
        parameters={
            "width": 8,
            "height": 8,
            "density": 0.75,
            "homophily": 0.5,
        },
    ).run()

    result.dataset.validate()

    assert result.status == "completed"
    assert result.dataset.schema_errors() == []
    assert any(record["metric"] == "mean_similarity" for record in result.dataset.model_records)
    assert any(record["metric"] == "unhappy_households" for record in result.dataset.model_records)


def test_sir_model_zoo_dataset_validates() -> None:
    result = Scenario(
        model=SIRModel,
        seed=42,
        steps=3,
        name="test-sir",
        parameters={
            "width": 8,
            "height": 8,
            "n_agents": 40,
            "initial_infected": 3,
            "infection_prob": 0.25,
            "recovery_prob": 0.05,
        },
    ).run()

    result.dataset.validate()

    assert result.status == "completed"
    assert result.dataset.schema_errors() == []
    assert any(record["metric"] == "susceptible" for record in result.dataset.model_records)
    assert any(record["metric"] == "infected" for record in result.dataset.model_records)
    assert any(record["metric"] == "recovered" for record in result.dataset.model_records)


def test_schelling_odd_document_exports() -> None:
    odd = build_schelling_odd()
    data = odd.to_dict()
    markdown = odd.to_markdown()

    assert data["schema_version"] == "abmforge.odd.v1"
    assert data["model"]["name"] == "SchellingModel"
    assert data["completeness"]["purpose"] is True
    assert "Schelling" in markdown or "segregation" in markdown


def test_sir_odd_document_exports() -> None:
    odd = build_sir_odd()
    data = odd.to_dict()
    markdown = odd.to_markdown()

    assert data["schema_version"] == "abmforge.odd.v1"
    assert data["model"]["name"] == "SIRModel"
    assert data["completeness"]["purpose"] is True
    assert "epidemic" in markdown


def test_model_zoo_manifest_and_schema_outputs(tmp_path: Path) -> None:
    result = Scenario(
        model=SIRModel,
        seed=42,
        steps=2,
        name="test-sir-artifacts",
        parameters={
            "width": 6,
            "height": 6,
            "n_agents": 20,
            "initial_infected": 2,
            "infection_prob": 0.2,
            "recovery_prob": 0.05,
        },
    ).run()

    output_dir = tmp_path / "sir-artifacts"
    result.dataset.write_csv(output_dir)
    result.dataset.write_schema(output_dir)
    ReproducibilityManifest.from_run_result(
        result,
        include_git=False,
        include_packages=False,
        include_command=False,
    ).write(output_dir)

    assert (output_dir / "runs.csv").exists()
    assert (output_dir / "model_records.csv").exists()
    assert (output_dir / "agent_records.csv").exists()
    assert (output_dir / "dataset_schema_v1.json").exists()
    assert (output_dir / "manifest.json").exists()

    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "abmforge.manifest.v1"
    assert manifest["dataset_schema_version"] == "abmforge.dataset.v1"
    assert manifest["record_counts"]["model_records"] > 0


def test_schelling_run_script_creates_research_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "schelling-script"

    completed = subprocess.run(
        [
            sys.executable,
            "model_zoo/schelling/run.py",
            "--width",
            "8",
            "--height",
            "8",
            "--density",
            "0.75",
            "--homophily",
            "0.5",
            "--seed",
            "42",
            "--steps",
            "3",
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "model_zoo=schelling" in completed.stdout
    assert "status=completed" in completed.stdout
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "dataset_schema_v1.json").exists()
    assert (output_dir / "ODD.md").exists()
    assert (output_dir / "runs.csv").exists()
    assert (output_dir / "model_records.csv").exists()


def test_sir_run_script_creates_research_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "sir-script"

    completed = subprocess.run(
        [
            sys.executable,
            "model_zoo/sir/run.py",
            "--width",
            "8",
            "--height",
            "8",
            "--n-agents",
            "40",
            "--initial-infected",
            "3",
            "--infection-prob",
            "0.25",
            "--recovery-prob",
            "0.05",
            "--seed",
            "42",
            "--steps",
            "3",
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "model_zoo=sir" in completed.stdout
    assert "status=completed" in completed.stdout
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "dataset_schema_v1.json").exists()
    assert (output_dir / "ODD.md").exists()
    assert (output_dir / "runs.csv").exists()
    assert (output_dir / "model_records.csv").exists()
