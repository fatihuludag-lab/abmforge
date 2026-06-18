from pathlib import Path

from abmforge.data.schema import DatasetSchemaV1


def test_dataset_schema_docs_include_current_schema_version() -> None:
    text = Path("docs/dataset-schema-v1.md").read_text(encoding="utf-8")

    assert DatasetSchemaV1.version in text


def test_dataset_schema_docs_include_all_current_tables() -> None:
    text = Path("docs/dataset-schema-v1.md").read_text(encoding="utf-8")

    for table_name in DatasetSchemaV1.tables:
        assert f"`{table_name}`" in text, table_name


def test_dataset_schema_docs_do_not_use_stale_draft_table_names() -> None:
    text = Path("docs/dataset-schema-v1.md").read_text(encoding="utf-8")

    stale_names = [
        "agent_state",
        "model_state",
        "event_log",
        "experiment_run",
    ]

    for stale_name in stale_names:
        assert stale_name not in text, stale_name
