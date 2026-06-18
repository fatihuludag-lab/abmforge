from abmforge.cli.main import main
from abmforge.data.dataset import Dataset
from abmforge.experiment.archive import ExperimentArchive


def _make_dataset() -> Dataset:
    dataset = Dataset(run_id="run-cli-summary")
    dataset.add_run(
        run_id="run-cli-summary",
        scenario="cli_summary_scenario",
        model_name="CLISummaryModel",
        parameters={"x": 1},
        seed=7,
        status="completed",
    )
    dataset.record_model(step=0, time=0.0, metric="count", value=1)
    return dataset


def test_cli_summarize_prints_archive_summary(tmp_path, capsys) -> None:
    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(_make_dataset(), format="json")

    main(["summarize", str(archive.path)])

    captured = capsys.readouterr()

    assert "ABMForge archive summary" in captured.out
    assert "Valid: yes" in captured.out
    assert "run_id: run-cli-summary" in captured.out
    assert "model_name: CLISummaryModel" in captured.out


def test_cli_summarize_json_prints_machine_readable_summary(tmp_path, capsys) -> None:
    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(_make_dataset(), format="json")

    main(["summarize", str(archive.path), "--json"])

    captured = capsys.readouterr()

    assert '"run_id": "run-cli-summary"' in captured.out
    assert '"valid": true' in captured.out
