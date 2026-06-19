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
