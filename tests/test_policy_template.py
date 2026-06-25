from __future__ import annotations

from pathlib import Path

from abmforge.cli.main import main
from abmforge.templates import create_project, list_templates


def test_list_templates_contains_policy() -> None:
    names = [template.name for template in list_templates()]

    assert "grid" in names
    assert "network" in names
    assert "epidemic" in names
    assert "segregation" in names
    assert "policy" in names


def test_create_policy_project(tmp_path: Path) -> None:
    project = create_project(tmp_path / "policy-study", template="policy")

    assert (project / "README.md").exists()
    assert (project / "configs" / "baseline.yaml").exists()
    assert (project / "configs" / "experiment.yaml").exists()
    assert (project / "model" / "__init__.py").exists()
    assert (project / "model" / "agents.py").exists()
    assert (project / "model" / "model.py").exists()
    assert (project / "tests" / "test_smoke.py").exists()


def test_scaffolded_policy_baseline_runs(tmp_path: Path, monkeypatch) -> None:
    project = create_project(tmp_path / "policy-run", template="policy")
    monkeypatch.chdir(project)

    main(
        [
            "run",
            "configs/baseline.yaml",
            "--archive",
            "outputs/baseline",
            "--overwrite",
        ]
    )

    assert (project / "outputs" / "baseline" / "manifest.json").exists()
    assert (project / "outputs" / "baseline" / "reports" / "run_summary.json").exists()


def test_scaffolded_policy_experiment_and_report_run(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = create_project(tmp_path / "policy-experiment", template="policy")
    experiment_yaml = project / "configs" / "experiment.yaml"
    text = experiment_yaml.read_text(encoding="utf-8")
    text = text.replace("count: 5", "count: 2")
    text = text.replace(
        "intervention_coverage: [0.20, 0.40, 0.60]",
        "intervention_coverage: [0.20, 0.60]",
    )
    experiment_yaml.write_text(text, encoding="utf-8")

    monkeypatch.chdir(project)

    main(
        [
            "experiment",
            "configs/experiment.yaml",
            "--archive",
            "outputs/experiment",
            "--overwrite",
        ]
    )
    main(["report", "outputs/experiment"])

    reports = project / "outputs" / "experiment" / "reports"

    assert (reports / "summary.md").exists()
    assert (reports / "metric_summary.csv").exists()
    assert (reports / "parameter_effects.csv").exists()
    assert (reports / "primary_metric_rankings.csv").exists()
