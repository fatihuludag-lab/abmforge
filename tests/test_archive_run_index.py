import json
from pathlib import Path

from abmforge.data.dataset import Dataset
from abmforge.experiment import ExperimentArchive, RunIndex
from abmforge.experiment.run_index import RUN_INDEX_SCHEMA_VERSION


def _dataset_with_run() -> Dataset:
    dataset = Dataset(run_id="run-001")
    dataset.add_run(
        run_id="run-001",
        scenario="baseline",
        model_name="ToyModel",
        parameters={"alpha": 0.2, "n": 10},
        seed=42,
        status="completed",
        started_at="2026-06-22T10:00:00+00:00",
        ended_at="2026-06-22T10:00:01+00:00",
        steps=5,
        stop_reason=None,
    )
    return dataset


def test_run_index_round_trips_from_dataset(tmp_path: Path) -> None:
    dataset = _dataset_with_run()

    index = RunIndex.from_dataset(dataset)
    path = index.write(tmp_path / "run_index.json")

    raw = json.loads(path.read_text(encoding="utf-8"))

    assert raw["schema_version"] == RUN_INDEX_SCHEMA_VERSION
    assert len(raw["entries"]) == 1

    loaded = RunIndex.read(path)
    entry = loaded.find("run-001")

    assert entry is not None
    assert entry.run_id == "run-001"
    assert entry.scenario == "baseline"
    assert entry.model_name == "ToyModel"
    assert entry.seed == 42
    assert entry.status == "completed"
    assert entry.steps == 5
    assert entry.parameters == {"alpha": 0.2, "n": 10}
    assert entry.archive_path == "."
    assert entry.dataset_path == "data"
    assert entry.manifest_path == "manifest.json"
    assert entry.dataset_schema_path == "dataset_schema.json"


def test_archive_write_run_outputs_creates_readable_run_index(tmp_path: Path) -> None:
    dataset = _dataset_with_run()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)

    assert archive.run_index_path.is_file()

    index = archive.read_run_index()
    entry = index.find("run-001")

    assert entry is not None
    assert entry.scenario == "baseline"
    assert entry.status == "completed"
    assert archive.validate() == []


def test_archive_validation_allows_missing_run_index_for_older_archives(
    tmp_path: Path,
) -> None:
    dataset = _dataset_with_run()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)
    archive.run_index_path.unlink()

    assert archive.validate() == []


def test_archive_validation_reports_invalid_run_index(tmp_path: Path) -> None:
    dataset = _dataset_with_run()
    archive = ExperimentArchive.create(tmp_path / "archive")

    archive.write_run_outputs(dataset)
    archive.run_index_path.write_text(
        json.dumps({"schema_version": RUN_INDEX_SCHEMA_VERSION, "entries": "bad"}),
        encoding="utf-8",
    )

    errors = archive.validate()

    assert any(error.startswith("Invalid run_index.json:") for error in errors)
