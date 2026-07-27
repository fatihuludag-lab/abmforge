import json

import pytest

from abmforge import __version__
from abmforge.cli.main import main


def test_cli_version(capsys) -> None:
    main(["--version"])
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_cli_info(capsys) -> None:
    main(["info"])
    captured = capsys.readouterr()
    assert "ABMForge" in captured.out
    assert __version__ in captured.out
    assert "Core objects" in captured.out


def test_cli_help(capsys) -> None:
    main([])
    captured = capsys.readouterr()
    assert "usage:" in captured.out


def test_cli_unknown_command() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["unknown"])

    assert exc_info.value.code == 2


def test_cli_run_scenario_writes_archive(tmp_path, monkeypatch, capsys) -> None:
    model_file = tmp_path / "toy_model.py"
    model_file.write_text(
        """
from abmforge import Model


class ToyModel(Model):
    def setup(self):
        self.record.metric("step", lambda model: model.steps)

    def step(self):
        pass
""",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
name: toy_cli
model: toy_model.ToyModel
run:
  seed: 123
  steps: 3
""",
        encoding="utf-8",
    )

    archive_path = tmp_path / "archive"

    main(
        [
            "run",
            str(scenario_file),
            "--archive",
            str(archive_path),
            "--overwrite",
        ]
    )

    captured = capsys.readouterr()
    assert "Run completed" in captured.out
    assert "Archive written" in captured.out

    assert (archive_path / "manifest.json").is_file()
    assert (archive_path / "dataset_schema.json").is_file()
    assert (archive_path / "data" / "runs.json").is_file()
    assert (archive_path / "data" / "model_records.jsonl").is_file()
    assert (archive_path / "reports" / "run_summary.json").is_file()
    assert (archive_path / "configs" / "scenario.yaml").is_file()

    manifest = json.loads((archive_path / "manifest.json").read_text(encoding="utf-8"))
    artifact_paths = {artifact["path"] for artifact in manifest["artifacts"]}

    assert "reports/run_summary.json" in artifact_paths
    assert manifest["artifact_count"] == len(manifest["artifacts"])

    main(["validate", str(archive_path)])

    captured = capsys.readouterr()
    assert "Archive validation passed" in captured.out


def test_cli_run_overwrite_preserves_existing_archive_when_write_fails(
    tmp_path,
    monkeypatch,
) -> None:
    from abmforge.experiment.archive import ExperimentArchive

    model_file = tmp_path / "failing_write_model.py"
    model_file.write_text(
        """
from abmforge import Model


class FailingWriteModel(Model):
    def step(self):
        pass
""",
        encoding="utf-8",
    )

    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
name: transactional_overwrite
model: failing_write_model.FailingWriteModel
run:
  seed: 123
  steps: 1
""",
        encoding="utf-8",
    )

    archive_path = tmp_path / "archive"
    archive_path.mkdir()
    marker = archive_path / "existing-result.txt"
    marker.write_text("preserve me", encoding="utf-8")

    def fail_write_run_outputs(self, dataset, *, format="json"):
        raise RuntimeError("simulated archive write failure")

    monkeypatch.setattr(
        ExperimentArchive,
        "write_run_outputs",
        fail_write_run_outputs,
    )
    monkeypatch.chdir(tmp_path)

    with pytest.raises(RuntimeError, match="simulated archive write failure"):
        main(
            [
                "run",
                str(scenario_file),
                "--archive",
                str(archive_path),
                "--overwrite",
            ]
        )

    assert marker.read_text(encoding="utf-8") == "preserve me"
    assert list(tmp_path.glob(".archive.staging-*")) == []
    assert list(tmp_path.glob(".archive.backup-*")) == []


def test_cli_run_overwrite_commits_new_archive_after_success(
    tmp_path,
    monkeypatch,
) -> None:
    model_file = tmp_path / "successful_overwrite_model.py"
    model_file.write_text(
        """
from abmforge import Model


class SuccessfulOverwriteModel(Model):
    def step(self):
        pass
""",
        encoding="utf-8",
    )

    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
name: successful_overwrite
model: successful_overwrite_model.SuccessfulOverwriteModel
run:
  seed: 321
  steps: 1
""",
        encoding="utf-8",
    )

    archive_path = tmp_path / "archive"
    archive_path.mkdir()
    marker = archive_path / "old-result.txt"
    marker.write_text("old archive", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    main(
        [
            "run",
            str(scenario_file),
            "--archive",
            str(archive_path),
            "--overwrite",
        ]
    )

    assert not marker.exists()
    assert (archive_path / "manifest.json").is_file()
    assert (archive_path / "data" / "runs.json").is_file()
    assert (archive_path / "reports" / "run_summary.json").is_file()
    assert list(tmp_path.glob(".archive.staging-*")) == []
    assert list(tmp_path.glob(".archive.backup-*")) == []


def test_cli_run_overwrite_rolls_back_when_summary_write_fails(
    tmp_path,
    monkeypatch,
) -> None:
    model_file = tmp_path / "summary_failure_model.py"
    model_file.write_text(
        """
from abmforge import Model


class SummaryFailureModel(Model):
    def step(self):
        pass
""",
        encoding="utf-8",
    )

    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
name: summary_failure
model: summary_failure_model.SummaryFailureModel
run:
  seed: 456
  steps: 1
""",
        encoding="utf-8",
    )

    archive_path = tmp_path / "archive"
    archive_path.mkdir()
    marker = archive_path / "existing-result.txt"
    marker.write_text("preserve me", encoding="utf-8")

    def fail_write_summary(result, archive):
        raise RuntimeError("simulated summary write failure")

    monkeypatch.setattr(
        "abmforge.cli.main._write_run_summary",
        fail_write_summary,
    )
    monkeypatch.chdir(tmp_path)

    with pytest.raises(RuntimeError, match="simulated summary write failure"):
        main(
            [
                "run",
                str(scenario_file),
                "--archive",
                str(archive_path),
                "--overwrite",
            ]
        )

    assert marker.read_text(encoding="utf-8") == "preserve me"
    assert list(tmp_path.glob(".archive.staging-*")) == []
    assert list(tmp_path.glob(".archive.backup-*")) == []
