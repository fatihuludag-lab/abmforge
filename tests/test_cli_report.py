from __future__ import annotations

from pathlib import Path

from abmforge.cli.main import build_parser, main
from abmforge.templates import create_project


def test_build_parser_includes_report_command() -> None:
    help_text = build_parser().format_help()

    assert "report" in help_text


def test_cli_report_runs_on_scaffolded_experiment(tmp_path, monkeypatch) -> None:
    project = create_project(tmp_path / "demo-study", template="grid")
    experiment_yaml = project / "configs" / "experiment.yaml"
    text = experiment_yaml.read_text(encoding="utf-8")
    text = text.replace("count: 10", "count: 2")
    text = text.replace(
        "transfer_probability: [0.20, 0.35, 0.50]",
        "transfer_probability: [0.20, 0.50]",
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

    output = Path("outputs") / "experiment" / "reports"

    assert (output / "summary.md").exists()
    assert (output / "metric_summary.csv").exists()
    assert (output / "run_status.csv").exists()
    assert (output / "failed_runs.csv").exists()
    assert (output / "parameter_effects.csv").exists()
    assert (output / "primary_metric_rankings.csv").exists()
