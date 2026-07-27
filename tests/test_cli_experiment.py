from __future__ import annotations

import json
from pathlib import Path

import pytest

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


def test_cli_experiment_fail_fast_writes_partial_archive(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    model_file = tmp_path / "partial_model.py"
    model_file.write_text(
        """
from abmforge import Model


class PartialFailureModel(Model):
    def setup(self):
        if self.parameters.get("should_fail", False):
            raise RuntimeError("intentional experiment failure")

    def step(self):
        pass
""",
        encoding="utf-8",
    )

    config_path = tmp_path / "experiment.yaml"
    config_path.write_text(
        """
name: partial-experiment
model: partial_model.PartialFailureModel
experiment:
  parameters:
    should_fail: [false, true, false]
  seeds: [1]
run:
  steps: 1
""",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    output = Path("outputs") / "partial-experiment"

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "experiment",
                str(config_path),
                "--archive",
                str(output),
                "--overwrite",
            ]
        )

    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Experiment failed" in captured.out
    assert "Partial output written" in captured.out

    assert (output / "manifest.json").is_file()
    assert (output / "dataset_schema.json").is_file()
    assert (output / "run_index.json").is_file()
    assert (output / "reports" / "experiment_summary.json").is_file()

    runs = json.loads((output / "data" / "runs.json").read_text(encoding="utf-8"))
    assert len(runs) == 2
    assert [run["status"] for run in runs] == [
        "completed",
        "failed",
    ]

    errors = [
        json.loads(line)
        for line in (output / "data" / "errors.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(errors) == 1
    assert errors[0]["recoverable"] is False

    summary = json.loads(
        (output / "reports" / "experiment_summary.json").read_text(encoding="utf-8")
    )
    assert summary["execution_status"] == "partial"
    assert summary["run_count_expected"] == 3
    assert summary["run_count_executed"] == 2
    assert summary["unexecuted_count"] == 1
    assert summary["result_summary"]["failed_count"] == 1

    main(["validate", str(output)])
    captured = capsys.readouterr()
    assert "Archive validation passed" in captured.out


def test_cli_experiment_continue_on_error_writes_all_runs_and_exits_nonzero(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    model_file = tmp_path / "continue_model.py"
    model_file.write_text(
        """
from abmforge import Model


class ContinueFailureModel(Model):
    def setup(self):
        if self.parameters.get("should_fail", False):
            raise RuntimeError("intentional continued failure")

    def step(self):
        pass
""",
        encoding="utf-8",
    )

    config_path = tmp_path / "experiment.yaml"
    config_path.write_text(
        """
name: continue-experiment
model: continue_model.ContinueFailureModel
experiment:
  parameters:
    should_fail: [false, true, false]
  seeds: [1]
run:
  steps: 1
""",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    output = Path("outputs") / "continue-experiment"

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "experiment",
                str(config_path),
                "--archive",
                str(output),
                "--overwrite",
                "--continue-on-error",
            ]
        )

    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Experiment completed with failures" in captured.out
    assert "Output written" in captured.out

    runs = json.loads((output / "data" / "runs.json").read_text(encoding="utf-8"))
    assert len(runs) == 3
    assert [run["status"] for run in runs] == [
        "completed",
        "failed",
        "completed",
    ]

    summary = json.loads(
        (output / "reports" / "experiment_summary.json").read_text(encoding="utf-8")
    )
    assert summary["execution_status"] == "completed_with_failures"
    assert summary["run_count_expected"] == 3
    assert summary["run_count_executed"] == 3
    assert summary["unexecuted_count"] == 0
    assert summary["result_summary"]["failed_count"] == 1
