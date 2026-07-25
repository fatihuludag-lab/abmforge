import csv

import pytest

from abmforge.data.dataset import Dataset
from abmforge.data.schema import DatasetSchemaV1, SchemaValidationError


def _csv_header(path):
    with path.open(newline="", encoding="utf-8") as f:
        return next(csv.reader(f))


def test_dataset_write_csv_creates_expected_files(tmp_path):
    dataset = Dataset(run_id="run-1")
    dataset.add_run(run_id="run-1", seed=42, status="completed")
    dataset.record_model(step=0, time=0.0, metric="wealth", value=10)
    dataset.record_agent(
        step=0,
        time=0.0,
        agent_id=1,
        agent_type="Person",
        variable="wealth",
        value=10,
    )
    dataset.record_event(
        step=0,
        time=0.0,
        event_id="event-1",
        owner=1,
        tags=["demo"],
        status="scheduled",
    )
    dataset.record_lifecycle(
        step=0,
        time=0.0,
        event="agent_created",
        agent_id=1,
        details={"agent_type": "Person"},
    )

    output_dir = dataset.write_csv(tmp_path)

    assert (output_dir / "runs.csv").exists()
    assert (output_dir / "model_records.csv").exists()
    assert (output_dir / "agent_records.csv").exists()
    assert (output_dir / "event_records.csv").exists()
    assert (output_dir / "lifecycle_records.csv").exists()

    assert "run-1" in (output_dir / "runs.csv").read_text(encoding="utf-8")
    assert "wealth" in (output_dir / "model_records.csv").read_text(encoding="utf-8")


def test_dataset_write_csv_handles_empty_tables(tmp_path):
    dataset = Dataset(run_id="empty-run")

    output_dir = dataset.write_csv(tmp_path)

    for table_name, table_schema in DatasetSchemaV1.tables.items():
        csv_path = output_dir / f"{table_name}.csv"

        assert csv_path.exists()
        assert _csv_header(csv_path) == [field.name for field in table_schema.fields]
        assert len(csv_path.read_text(encoding="utf-8").splitlines()) == 1


def test_dataset_write_csv_uses_schema_headers_before_extra_fields(tmp_path):
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="custom",
        custom_metric="kept",
    )

    output_dir = dataset.write_csv(tmp_path)
    header = _csv_header(output_dir / "runs.csv")
    schema_fields = [field.name for field in DatasetSchemaV1.tables["runs"].fields]

    assert header[: len(schema_fields)] == schema_fields
    assert "custom_metric" in header[len(schema_fields) :]


@pytest.mark.parametrize(
    "writer_name",
    [
        "write_json",
        "write_csv",
    ],
)
def test_dataset_export_rejects_schema_invalid_records(
    tmp_path,
    writer_name: str,
) -> None:
    dataset = Dataset(run_id="run-1")
    dataset.runs.append(
        {
            "status": "completed",
        }
    )

    writer = getattr(dataset, writer_name)

    with pytest.raises(
        SchemaValidationError,
        match=r"runs\[0\]\.run_id: missing required field",
    ):
        writer(tmp_path / writer_name)


@pytest.mark.parametrize(
    "writer_name",
    [
        "write_json",
        "write_csv",
    ],
)
@pytest.mark.parametrize(
    "invalid_time",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_dataset_export_rejects_non_finite_numeric_fields(
    tmp_path,
    writer_name: str,
    invalid_time: float,
) -> None:
    dataset = Dataset(run_id="run-1")
    dataset.record_model(
        step=0,
        time=invalid_time,
        metric="wealth",
        value=10,
    )

    writer = getattr(dataset, writer_name)

    with pytest.raises(
        SchemaValidationError,
        match=r"model_records\[0\]\.time: expected finite number",
    ):
        writer(tmp_path / writer_name)
