from __future__ import annotations

from pathlib import Path

from abmforge.cli.main import build_parser, main
from abmforge.templates import create_project


def test_build_parser_includes_experiment_command() -> None:
    help_text = build_parser().format_help()

    assert "experiment" in help_text


def test_cli_experiment_runs_scaffolded_project(tmp_path, monkeypatch) -> None:
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

    output = Path("outputs") / "experiment"

    assert (output / "configs" / "experiment.yaml").exists()
    assert (output / "data").exists()
    assert (output / "data" / "runs.json").exists()
    assert (output / "data" / "runs.csv").exists()
    assert (output / "manifest.json").exists()
    assert (output / "dataset_schema.json").exists()
    assert (output / "run_index.json").exists()
    assert (output / "reports" / "experiment_summary.json").exists()
    assert (output / "reports" / "README_RESULTS.md").exists()

    main(["validate", "outputs/experiment"])
