from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from model import ThresholdAdoptionModel

from abmforge import ODDDocument


def build_odd_document() -> ODDDocument:
    """Build the ODD-style documentation artifact for the example study."""

    odd = ODDDocument.from_model(
        ThresholdAdoptionModel,
        title="ODD documentation for the threshold-adoption reference study",
        purpose=(
            "Document a compact stochastic threshold-adoption model used to "
            "demonstrate the ABMForge research workflow: experiment YAML, "
            "multi-run archive, validation, summaries, reports, ODD metadata, "
            "and lightweight analysis artifacts."
        ),
        authors=["Fatih Uludağ"],
        entities=["Consumer"],
        scales={
            "time": (
                "Discrete simulation steps; one step represents one abstract adoption update cycle."
            ),
            "space": (
                "No explicit spatial environment; agents interact through sampled peer exposure."
            ),
            "population": (
                "A fixed synthetic consumer population configured by the experiment YAML."
            ),
        },
        process_overview=[
            "The model initializes consumers with adoption states and thresholds.",
            "At each step, non-adopters sample peers using the model-level RNG.",
            (
                "A consumer adopts when peer influence plus advertising reaches "
                "the consumer threshold."
            ),
            "Model-level and agent-level observations are recorded into the ABMForge dataset.",
            "The experiment runs a parameter grid across multiple deterministic seeds.",
        ],
        design_concepts={
            "emergence": (
                "Aggregate adoption curves emerge from heterogeneous thresholds, "
                "stochastic peer sampling, and asynchronous agent activation."
            ),
            "stochasticity": (
                "Initial adoption states, thresholds, peer samples, and activation order "
                "are controlled by ABMForge seeded random number generation."
            ),
            "observation": (
                "The study records adoption share, adopter count, new adoptions, "
                "mean threshold, and selected agent-level states."
            ),
            "sensitivity": (
                "The experiment varies peer influence and adoption threshold to "
                "demonstrate parameterized multi-run workflows."
            ),
        },
        initialization=[
            (
                "Population size, initial adoption rate, peer sample size, threshold jitter, "
                "advertising level, peer influence, and adoption threshold are loaded "
                "from experiment YAML."
            ),
            "Each consumer receives an adopted state and a bounded threshold in [0, 1].",
        ],
        input_data=[
            {
                "name": "configs/experiment.yaml",
                "description": (
                    "Self-contained synthetic experiment configuration with parameter grid, "
                    "seeds, run length, and primary metric."
                ),
                "source": "Repository example configuration",
            }
        ],
        submodels=[
            {
                "name": "Consumer adoption decision",
                "description": (
                    "A non-adopter adopts when weighted peer adoption exposure plus "
                    "advertising is greater than or equal to the consumer threshold."
                ),
                "source": "examples/reproducible_study/model.py::Consumer.step",
            },
            {
                "name": "Experiment workflow",
                "description": (
                    "ABMForge runs a deterministic seed/parameter grid and writes a "
                    "validated experiment archive."
                ),
                "source": "examples/reproducible_study/reproduce.py",
            },
        ],
        decision_processes=[
            {
                "name": "Adoption threshold decision",
                "actor": "Consumer",
                "description": (
                    "The agent compares peer adoption exposure and advertising against "
                    "its threshold."
                ),
                "inputs": [
                    "peer_adoption_share",
                    "peer_influence",
                    "advertising",
                    "threshold",
                ],
                "outputs": ["adopted", "new_adoptions"],
                "notes": (
                    "This is a stylized synthetic decision rule, not an empirical behavioral claim."
                ),
            }
        ],
        metadata={
            "example": "examples/reproducible_study",
            "primary_metric": "adoption_share",
            "research_status": "reference workflow example; not an empirical study",
        },
    )
    odd.add_state_variable(
        "Consumer",
        "adopted",
        description="Whether the consumer has adopted the synthetic product or behavior.",
        kind="bool",
        unit="state",
    )
    odd.add_state_variable(
        "Consumer",
        "threshold",
        description="Minimum adoption signal required for adoption.",
        kind="float",
        unit="share",
    )
    return odd


def write_research_documentation(archive_path: str | Path) -> dict[str, str]:
    """Write reviewer-facing documentation artifacts into an archive report directory."""

    archive = Path(archive_path)
    reports = archive / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    odd = build_odd_document()
    odd_markdown = odd.write_markdown(reports / "ODD.md")
    odd_json = odd.write_json(reports / "ODD.json")
    protocol = _write_research_protocol(reports / "research_protocol.md")
    manifest = _write_artifact_manifest(
        archive,
        [
            odd_markdown,
            odd_json,
            protocol,
            archive / "manifest.json",
            archive / "dataset_schema.json",
            archive / "run_index.json",
            reports / "experiment_summary.json",
            reports / "summary.md",
            reports / "reproducible_study_summary.csv",
            reports / "reproducible_study_adoption_curve.csv",
            reports / "reproducible_study_adoption_curve.svg",
        ],
    )

    return {
        "odd_markdown": str(odd_markdown.relative_to(archive)),
        "odd_json": str(odd_json.relative_to(archive)),
        "research_protocol": str(protocol.relative_to(archive)),
        "artifact_manifest": str(manifest.relative_to(archive)),
    }


def _write_research_protocol(path: Path) -> Path:
    path.write_text(
        """# Threshold-Adoption Reference Study Protocol

## Purpose

This protocol describes the compact reproducible-study example included with
ABMForge. The example is a synthetic workflow demonstration, not an empirical
claim about real adoption behavior.

## Research question

How can a stochastic agent-based model be packaged as an inspectable
ABMForge research artifact using experiment YAML, deterministic seeds, archive
validation, summary reports, ODD-style model documentation, and lightweight
analysis outputs?

## Model summary

The model contains consumer agents with heterogeneous adoption thresholds. A
non-adopter samples peers at each step. Adoption occurs when the weighted peer
adoption signal plus an advertising term reaches the consumer threshold.

## Experimental design

The experiment varies:

- `peer_influence`
- `adoption_threshold`

The experiment also runs multiple deterministic seeds so stochastic variation
is represented in the resulting archive.

## Primary metric

The primary metric is `adoption_share`, recorded as a model-level time series.

## Reproducibility contract

A reproduced archive should include:

- `manifest.json`
- `dataset_schema.json`
- `run_index.json`
- copied experiment configuration
- model-level and agent-level records
- summary reports
- ODD Markdown and JSON artifacts
- this research protocol
- an artifact manifest

## Limitations

This example is deliberately small. It is designed to demonstrate workflow
structure, not empirical calibration, external validation, or a substantive
scientific claim.
""",
        encoding="utf-8",
    )
    return path


def _write_artifact_manifest(archive: Path, artifacts: list[Path]) -> Path:
    manifest_path = archive / "reports" / "artifact_manifest.json"
    payload: dict[str, Any] = {
        "schema_version": "abmforge.example_artifacts.v1",
        "example": "examples/reproducible_study",
        "purpose": "Reviewer-facing manifest for the reference reproducible study.",
        "artifacts": [],
    }

    for artifact in artifacts:
        payload["artifacts"].append(
            {
                "path": str(artifact.relative_to(archive)),
                "exists": artifact.exists(),
                "size_bytes": artifact.stat().st_size if artifact.exists() else None,
            }
        )

    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest_path
