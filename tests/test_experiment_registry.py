from __future__ import annotations

from abmforge.experiment.archive import ExperimentArchive
from abmforge.experiment.registry import ExperimentRegistry


def test_experiment_registry_records_runs_snapshots_and_validations(tmp_path):
    registry = ExperimentRegistry(experiment_id="exp-1")

    registry.add_run(run_id="run-1", status="completed")
    registry.add_snapshot(
        snapshot_id="snapshot-1",
        run_id="run-1",
        snapshot_hash="abc",
    )
    registry.add_validation(
        validation_id="validation-1",
        valid=True,
        original_hash="abc",
        replayed_hash="abc",
    )

    assert registry.experiment_id == "exp-1"
    assert registry.runs[0]["run_id"] == "run-1"
    assert registry.snapshots[0]["snapshot_id"] == "snapshot-1"
    assert registry.validations[0]["valid"] is True

    path = tmp_path / "registry.json"
    registry.write(path)

    loaded = ExperimentRegistry.read(path)

    assert loaded.to_dict()["experiment_id"] == "exp-1"
    assert loaded.runs[0]["run_id"] == "run-1"
    assert loaded.snapshots[0]["snapshot_hash"] == "abc"


def test_experiment_archive_creates_and_reads_registry(tmp_path):
    archive = ExperimentArchive.create(tmp_path / "archive")

    registry = archive.create_registry(experiment_id="exp-1")
    registry.add_run(run_id="run-1", status="completed")
    registry.write(archive.registry_path)

    loaded = archive.read_registry()

    assert archive.registry_path.exists()
    assert loaded.experiment_id == "exp-1"
    assert loaded.runs[0]["run_id"] == "run-1"


def test_experiment_archive_ensure_registry_creates_missing_registry(tmp_path):
    archive = ExperimentArchive.create(tmp_path / "archive")

    registry = archive.ensure_registry()

    assert archive.registry_path.exists()
    assert registry.experiment_id.startswith("experiment-")


def test_experiment_archive_ensure_registry_reads_existing_registry(tmp_path):
    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.create_registry(experiment_id="exp-existing")

    registry = archive.ensure_registry()

    assert registry.experiment_id == "exp-existing"
