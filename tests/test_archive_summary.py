from abmforge.data.dataset import Dataset
from abmforge.experiment.archive import ExperimentArchive
from abmforge.experiment.summary import format_archive_summary, summarize_archive


def _make_dataset() -> Dataset:
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="summary_scenario",
        model_name="SummaryModel",
        parameters={"x": 1},
        seed=42,
        status="completed",
    )
    dataset.record_model(step=0, time=0.0, metric="count", value=1)
    return dataset


def test_summarize_archive_returns_manifest_and_file_counts(tmp_path) -> None:
    dataset = _make_dataset()

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="json")

    summary = summarize_archive(archive.path)

    assert summary["valid"] is True
    assert summary["run_id"] == "run-1"
    assert summary["status"] == "completed"
    assert summary["scenario"] == "summary_scenario"
    assert summary["model_name"] == "SummaryModel"
    assert summary["seed"] == 42

    assert summary["record_counts"]["manifest"]["runs"] == 1
    assert summary["record_counts"]["manifest"]["model_records"] == 1

    assert summary["record_counts"]["files"]["runs"] == 1
    assert summary["record_counts"]["files"]["model_records"] == 1


def test_format_archive_summary_contains_key_fields(tmp_path) -> None:
    dataset = _make_dataset()

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="json")

    summary = summarize_archive(archive.path)
    text = format_archive_summary(summary)

    assert "ABMForge archive summary" in text
    assert "Valid: yes" in text
    assert "run_id: run-1" in text
    assert "model_name: SummaryModel" in text
    assert "model_records" in text
