from abmforge.experiment.archive import ExperimentArchive


def test_archive_write_scenario_file_copies_yaml_to_configs_dir(tmp_path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
name: test_scenario
model: example.Model
run:
  steps: 1
""",
        encoding="utf-8",
    )

    archive = ExperimentArchive.create(tmp_path / "archive")
    copied_path = archive.write_scenario_file(scenario_file)

    assert copied_path == archive.configs_dir / "scenario.yaml"
    assert copied_path.is_file()
    assert copied_path.read_text(encoding="utf-8") == scenario_file.read_text(encoding="utf-8")


def test_archive_write_scenario_file_rejects_missing_file(tmp_path) -> None:
    archive = ExperimentArchive.create(tmp_path / "archive")

    missing_file = tmp_path / "missing.yaml"

    try:
        archive.write_scenario_file(missing_file)
    except FileNotFoundError as exc:
        assert "Scenario file does not exist" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")
