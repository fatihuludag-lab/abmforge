import pytest

from abmforge.core.status import COMPLETED, CREATED, FAILED, RUNNING, STOPPED
from abmforge.data.dataset import Dataset
from abmforge.data.schema import DatasetSchemaV1, SchemaValidationError


def _dataset_with_status(status: str | None) -> Dataset:
    dataset = Dataset(run_id="run-status-test")
    dataset.add_run(
        run_id="run-status-test",
        scenario="status_scenario",
        model_name="StatusModel",
        parameters={},
        seed=1,
        status=status,
    )
    return dataset


@pytest.mark.parametrize(
    "status",
    [
        CREATED,
        RUNNING,
        COMPLETED,
        STOPPED,
        FAILED,
        None,
    ],
)
def test_dataset_schema_accepts_known_run_statuses(status: str | None) -> None:
    dataset = _dataset_with_status(status)

    assert dataset.schema_errors() == []


def test_dataset_schema_rejects_unknown_run_status() -> None:
    dataset = _dataset_with_status("unknown")

    errors = dataset.schema_errors()

    assert any("runs[0].status: expected one of" in error for error in errors)
    assert any("unknown" in error for error in errors)


def test_dataset_validate_raises_for_unknown_run_status() -> None:
    dataset = _dataset_with_status("unknown")

    with pytest.raises(SchemaValidationError, match=r"runs\[0\]\.status"):
        dataset.validate()


def test_dataset_schema_exports_run_status_enum() -> None:
    schema = DatasetSchemaV1.to_dict()
    runs_fields = schema["tables"]["runs"]["fields"]

    status_fields = [field for field in runs_fields if field["name"] == "status"]

    assert len(status_fields) == 1
    assert {
        CREATED,
        RUNNING,
        COMPLETED,
        STOPPED,
        FAILED,
    } == set(status_fields[0]["enum"])
