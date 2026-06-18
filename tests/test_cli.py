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

    monkeypatch.syspath_prepend(str(tmp_path))

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

    main(["validate", str(archive_path)])

    captured = capsys.readouterr()
    assert "Archive validation passed" in captured.out
