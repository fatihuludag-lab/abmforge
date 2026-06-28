from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scheduler_metadata_is_documented() -> None:
    scheduling_doc = (ROOT / "docs" / "scheduling.md").read_text(encoding="utf-8")
    replay_doc = (ROOT / "docs" / "replay.md").read_text(encoding="utf-8")

    required_scheduling_terms = [
        "Scheduler metadata",
        "to_metadata()",
        "scheduler-metadata-v1",
        "StagedActivation.to_metadata()",
        "not a scheduler restore contract",
    ]
    for term in required_scheduling_terms:
        assert term in scheduling_doc

    required_replay_terms = [
        "`scheduler`",
        "scheduler-metadata-v1",
        "attached",
        "not a scheduler restore contract",
        "Model.from_snapshot",
    ]
    for term in required_replay_terms:
        assert term in replay_doc
