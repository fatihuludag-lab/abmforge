import pytest

from abmforge.cli.main import main


def test_cli_run_invalid_scenario_prints_clean_validation_error(
    tmp_path,
    capsys,
) -> None:
    scenario_file = tmp_path / "invalid.yaml"
    scenario_file.write_text(
        """
name: invalid_scenario
parameters:
  x: 1
run:
  steps: 1
""",
        encoding="utf-8",
    )

    archive_path = tmp_path / "archive"

    with pytest.raises(SystemExit) as exc_info:
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

    assert exc_info.value.code == 2
    assert "Scenario validation failed:" in captured.out
    assert "Missing required field: model" in captured.out
    assert not archive_path.exists()


def test_cli_run_invalid_steps_prints_clean_validation_error(
    tmp_path,
    capsys,
) -> None:
    scenario_file = tmp_path / "invalid_steps.yaml"
    scenario_file.write_text(
        """
name: invalid_steps
model: tests.test_scenario_yaml_validation.ScenarioValidationModel
run:
  steps: invalid
""",
        encoding="utf-8",
    )

    archive_path = tmp_path / "archive"

    with pytest.raises(SystemExit) as exc_info:
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

    assert exc_info.value.code == 2
    assert "Scenario validation failed:" in captured.out
    assert "Field 'run.steps' must be an integer" in captured.out
    assert not archive_path.exists()
