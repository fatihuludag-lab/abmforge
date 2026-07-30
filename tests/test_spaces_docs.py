from __future__ import annotations

from pathlib import Path

DOC_PATH = Path("docs/spaces.md")


def test_spaces_docs_describe_builtin_spaces() -> None:
    text = DOC_PATH.read_text(
        encoding="utf-8",
    )

    for name in [
        "GridWorld",
        "ContinuousSpace",
        "GISSpace",
        "NetworkSpace",
    ]:
        assert name in text


def test_spaces_docs_describe_referential_integrity_contract() -> None:
    text = DOC_PATH.read_text(
        encoding="utf-8",
    )
    normalized = " ".join(text.split())

    expected = [
        "[Simulation Semantics V1](simulation-semantics-v1.md)",
        "## Referential-integrity contract",
        "same agent object",
        "same identifier but a different object",
        "already belongs to another space",
        "clear both `agent.pos` and `agent.world`",
        "`space.remove(agent)` is spatial unplacement only",
        "`AgentCollection.remove(...)` or `Model.remove_agent(...)`",
        "failed placement or removal request leaves existing indexes unchanged",
    ]

    for statement in expected:
        assert statement in normalized
