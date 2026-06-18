import json

from abmforge.data.dataset import Dataset
from abmforge.experiment.archive import ExperimentArchive


def _make_dataset() -> Dataset:
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="test_scenario",
        model_name="TestModel",
        parameters={"x": 1},
        seed=42,
        status="completed",
    )
    dataset.record_model(step=0, time=0.0, metric="count", value=1)
    return dataset


def test_archive_validate_checks_json_record_counts_and_hashes(tmp_path) -> None:
    dataset = _make_dataset()

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="json")

    assert archive.validate() == []


def test_archive_validate_detects_tampered_json_dataset_file(tmp_path) -> None:
    dataset = _make_dataset()

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="json")

    model_records_path = archive.data_dir / "model_records.jsonl"
    model_records_path.write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "step": 0,
                "time": 0.0,
                "metric": "count",
                "value": 999,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    errors = archive.validate()

    assert any("record_hashes mismatch for model_records" in error for error in errors)


def test_archive_validate_detects_missing_json_dataset_table(tmp_path) -> None:
    dataset = _make_dataset()

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="json")

    (archive.data_dir / "errors.jsonl").unlink()

    errors = archive.validate()

    assert "Missing dataset table file: data/errors.jsonl" in errors


def test_archive_validate_detects_tampered_dataset_schema(tmp_path) -> None:
    dataset = _make_dataset()

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset, format="json")

    schema = json.loads(archive.dataset_schema_path.read_text(encoding="utf-8"))
    schema["schema_version"] = "tampered"
    archive.dataset_schema_path.write_text(
        json.dumps(schema, indent=2),
        encoding="utf-8",
    )

    errors = archive.validate()

    assert any("dataset_schema_hash mismatch" in error for error in errors)
