from pathlib import Path


def test_agent_lifecycle_docs_include_statuses_and_removal_contract() -> None:
    text = Path("docs/agent-lifecycle.md").read_text(encoding="utf-8")

    assert "`active`" in text
    assert "`removed`" in text
    assert "agent.remove()" in text
    assert "model.remove_agent" in text
    assert "lifecycle_status" in text


def test_agent_lifecycle_docs_include_removal_side_effects() -> None:
    text = Path("docs/agent-lifecycle.md").read_text(encoding="utf-8")

    assert "agent.is_alive = False" in text
    assert "removed from model.agents" in text
    assert "removed from model.world" in text
    assert "pending events owned by the agent are cancelled" in text
    assert "agent_removed" in text


def test_agent_lifecycle_docs_include_reproducibility_guidance() -> None:
    text = Path("docs/agent-lifecycle.md").read_text(encoding="utf-8")

    assert "Lifecycle records" in text
    assert "Event records" in text
    assert "Snapshot behaviour" in text
    assert "Research reproducibility recommendation" in text


def test_agent_lifecycle_docs_describe_managed_collection_removal() -> None:
    text = Path("docs/agent-lifecycle.md").read_text(
        encoding="utf-8",
    )
    normalized = " ".join(text.split())

    expected = [
        "`AgentCollection.remove(...)` and `Model.remove_agent(...)`",
        "same managed lifecycle contract",
        "active living agents",
        "Repeated removal raises `KeyError`",
        "spatial cleanup completes before lifecycle mutation",
        "`space.remove(agent)` performs spatial unplacement only",
        "does not remove the agent from `model.agents`",
        "same identifier but a different object",
    ]

    for statement in expected:
        assert statement in normalized

    obsolete = [
        "direct collection removal does not replace the broader cleanup",
        "direct collection removal changes collection membership only",
    ]

    for statement in obsolete:
        assert statement not in normalized
