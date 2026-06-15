from __future__ import annotations

import json

import pytest

from abmforge import DatasetSchemaV1, ReproducibilityManifest, SchemaValidationError
from abmforge.data.dataset import Dataset


def _valid_dataset() -> Dataset:
    dataset = Dataset(run_id="run-schema-test")

    dataset.add_run(
        run_id="run-schema-test",
        scenario="schema-demo",
        model_name="SchemaDemoModel",
        parameters={"alpha": 0.1},
        seed=42,
        status="completed",
        steps=1,
    )
    dataset.record_model(
        step=0,
        time=0.0,
        metric="population",
        value=10,
    )
    dataset.record_agent(
        step=0,
        time=0.0,
        agent_id=1,
        agent_type="Person",
        variable="wealth",
        value=5.0,
    )
    dataset.record_event(
        step=0,
        time=0.0,
        event_id="event-1",
        owner=1,
        tags=["demo"],
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


def test_dataset_schema_v1_contains_expected_tables() -> None:
    assert DatasetSchemaV1.version == "abmforge.dataset.v1"

    assert DatasetSchemaV1.table_names() == (
        "runs",
        "model_records",
        "agent_records",
        "event_records",
        "lifecycle_records",
        "errors",
    )


def test_valid_dataset_passes_schema_validation() -> None:
    dataset = _valid_dataset()

    errors = DatasetSchemaV1.validate_dataset(dataset, raise_on_error=False)

    assert errors == []


def test_dataset_validate_method_passes_for_valid_dataset() -> None:
    dataset = _valid_dataset()

    dataset.validate()

    assert dataset.schema_errors() == []
    assert dataset.schema_version == "abmforge.dataset.v1"


def test_invalid_dataset_raises_schema_validation_error() -> None:
    dataset = _valid_dataset()
    dataset.model_records.append(
        {
            "run_id": "run-schema-test",
            "step": "not-an-integer",
            "time": 0.0,
            "metric": "bad_metric",
            "value": 1,
        }
    )

    with pytest.raises(SchemaValidationError) as exc_info:
        DatasetSchemaV1.validate_dataset(dataset)

    assert "model_records[1].step" in str(exc_info.value)
    assert "expected integer" in str(exc_info.value)


def test_missing_required_field_is_reported() -> None:
    errors = DatasetSchemaV1.validate_record(
        "model_records",
        {
            "run_id": "run-schema-test",
            "step": 0,
            "time": 0.0,
            "value": 1,
        },
        raise_on_error=False,
    )

    assert any("metric" in error for error in errors)


def test_unknown_table_raises_key_error() -> None:
    with pytest.raises(KeyError, match="Unknown dataset table"):
        DatasetSchemaV1.validate_record("unknown_table", {}, raise_on_error=False)


def test_schema_can_be_written_to_directory(tmp_path) -> None:  # type: ignore[no-untyped-def]
    output_path = DatasetSchemaV1.write(tmp_path)

    assert output_path.name == "dataset_schema_v1.json"
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["schema_version"] == "abmforge.dataset.v1"
    assert "runs" in data["tables"]
    assert "errors" in data["tables"]


def test_dataset_write_schema(tmp_path) -> None:  # type: ignore[no-untyped-def]
    dataset = _valid_dataset()

    output_path = dataset.write_schema(tmp_path)

    assert output_path.exists()
    assert output_path.name == "dataset_schema_v1.json"


def test_manifest_includes_dataset_schema_metadata() -> None:
    dataset = _valid_dataset()

    manifest = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
    )
    data = manifest.to_dict()

    assert data["dataset_schema_version"] == "abmforge.dataset.v1"
    assert data["dataset_schema_hash"]
