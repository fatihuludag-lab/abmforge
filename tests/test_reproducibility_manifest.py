from __future__ import annotations

import json

import abmforge
from abmforge import Model, ReproducibilityManifest, Scenario
from abmforge.data.dataset import Dataset


class EmptyModel(Model):
    """Minimal model used for manifest tests."""


def _sample_dataset() -> Dataset:
    dataset = Dataset(run_id="run-test")
    dataset.add_run(
        run_id="run-test",
        scenario="demo",
        model_name="DemoModel",
        parameters={"alpha": 0.1, "beta": 2},
        seed=42,
        status="completed",
    )
    dataset.record_model(step=0, time=0.0, metric="population", value=10)
    dataset.record_agent(
        step=0,
        time=0.0,
        agent_id=1,
        agent_type="Person",
        variable="wealth",
        value=5,
    )
    dataset.record_event(
        step=0,
        time=0.0,
        event_id="event-1",
        owner=1,
        tags=["test"],
        status="executed",
    )
    dataset.record_lifecycle(
        step=0,
        time=0.0,
        event="created",
        agent_id=1,
        details={"agent_type": "Person"},
    )
    return dataset


def test_manifest_from_dataset_contains_required_metadata() -> None:
    dataset = _sample_dataset()

    manifest = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
        metadata={"purpose": "unit-test"},
    )
    data = manifest.to_dict()

    assert data["schema_version"] == "abmforge.manifest.v1"
    assert data["abmforge_version"] == abmforge.__version__
    assert data["run_id"] == "run-test"
    assert data["scenario"] == "demo"
    assert data["model_name"] == "DemoModel"
    assert data["seed"] == 42
    assert data["status"] == "completed"
    assert data["parameters_hash"] is not None
    assert data["record_counts"]["runs"] == 1
    assert data["record_counts"]["model_records"] == 1
    assert data["record_counts"]["agent_records"] == 1
    assert data["record_counts"]["event_records"] == 1
    assert data["record_counts"]["lifecycle_records"] == 1
    assert data["n_model_records"] == 1
    assert data["n_agent_records"] == 1
    assert data["n_event_records"] == 1
    assert data["n_lifecycle_records"] == 1
    assert data["git"] is None
    assert data["packages"] is None
    assert data["metadata"]["purpose"] == "unit-test"


def test_manifest_write_to_directory(tmp_path) -> None:  # type: ignore[no-untyped-def]
    dataset = _sample_dataset()
    manifest = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
    )

    output_path = manifest.write(tmp_path)

    assert output_path.name == "manifest.json"
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["schema_version"] == "abmforge.manifest.v1"
    assert data["run_id"] == "run-test"
    assert data["n_model_records"] == 1


def test_dataset_write_manifest_uses_manifest_v1(tmp_path) -> None:  # type: ignore[no-untyped-def]
    dataset = _sample_dataset()

    output_path = dataset.write_manifest(tmp_path)
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["schema_version"] == "abmforge.manifest.v1"
    assert data["abmforge_version"] == abmforge.__version__
    assert data["run_id"] == "run-test"
    assert data["record_counts"]["model_records"] == 1


def test_manifest_from_run_result() -> None:
    result = Scenario(model=EmptyModel, seed=123, steps=0, name="manifest-test").run()

    manifest = ReproducibilityManifest.from_run_result(
        result,
        include_git=False,
        include_packages=False,
        include_command=False,
    )
    data = manifest.to_dict()

    assert data["schema_version"] == "abmforge.manifest.v1"
    assert data["run_id"] == result.run_id
    assert data["abmforge_version"] == abmforge.__version__
    assert data["metadata"]["run_result_status"] == result.status
    assert data["metadata"]["run_result_steps"] == result.steps


def test_manifest_content_hash_is_stable_for_same_content() -> None:
    dataset = _sample_dataset()

    manifest_a = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
    )
    manifest_b = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
    )

    assert manifest_a.record_hashes == manifest_b.record_hashes
