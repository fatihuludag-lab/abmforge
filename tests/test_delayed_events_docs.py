from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_delayed_events_doc_exists_and_is_in_mkdocs_nav() -> None:
    doc = (ROOT / "docs" / "delayed-events.md").read_text(encoding="utf-8")
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Delayed Events" in doc
    assert "schedule_after" in doc
    assert "schedule_at" in doc
    assert "pending_events" in doc
    assert "next_event_time" in doc
    assert "Model.from_snapshot" in doc
    assert "delayed-events.md" in mkdocs
