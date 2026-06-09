from abmforge.data.dataset import Dataset


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

    assert (output_dir / "runs.csv").read_text(encoding="utf-8") == ""
    assert (output_dir / "model_records.csv").read_text(encoding="utf-8") == ""
