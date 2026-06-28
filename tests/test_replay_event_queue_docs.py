from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_replay_docs_describe_event_queue_metadata_and_limitations() -> None:
    doc = (ROOT / "docs" / "replay.md").read_text(encoding="utf-8")

    required_terms = [
        "Event queue metadata",
        "`event_queue`",
        "event-queue-metadata-v1",
        "callback_restore_supported",
        "not a full event replay contract",
        "Model.from_snapshot",
    ]

    for term in required_terms:
        assert term in doc
