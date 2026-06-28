from __future__ import annotations

from dataclasses import dataclass

from abmforge import (
    AdvanceableAgent,
    Agent,
    AgentID,
    AgentLike,
    Model,
    StatefulAgent,
    SteppableAgent,
)
from abmforge.core import AgentLike as CoreAgentLike


@dataclass
class ConsumerState:
    adopted: bool
    threshold: float


class Consumer(Agent):
    state: ConsumerState

    def step(self) -> None:
        self.state.adopted = True


class AdvancingConsumer(Consumer):
    def advance(self) -> None:
        self.state.threshold = min(1.0, self.state.threshold + 0.1)


def test_agent_protocols_are_runtime_checkable() -> None:
    model = Model(seed=123)
    agent = Consumer(
        model,
        1,
        state=ConsumerState(adopted=False, threshold=0.5),
    )

    assert isinstance(agent.unique_id, AgentID)
    assert isinstance(agent, AgentLike)
    assert isinstance(agent, CoreAgentLike)
    assert isinstance(agent, SteppableAgent)
    assert isinstance(agent, StatefulAgent)
    assert not isinstance(agent, AdvanceableAgent)


def test_advanceable_agent_protocol_detects_advance_method() -> None:
    model = Model(seed=123)
    agent = AdvancingConsumer(
        model,
        "consumer-1",
        state=ConsumerState(adopted=False, threshold=0.5),
    )

    assert isinstance(agent, AdvanceableAgent)


def test_agent_collection_preserves_concrete_agent_types() -> None:
    model = Model(seed=123)

    created = model.agents.create(
        Consumer,
        n=2,
        state=ConsumerState(adopted=False, threshold=0.5),
    )
    selected = model.agents.by_type(Consumer)

    assert selected == created
    assert all(isinstance(agent, Consumer) for agent in selected)
    assert all(isinstance(agent, StatefulAgent) for agent in selected)


def test_typed_agent_docs_are_in_mkdocs_nav() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    docs = (root / "docs" / "typed-agents.md").read_text(encoding="utf-8")
    mkdocs = (root / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Typed Agents" in docs
    assert "abmforge.core.protocols" in docs
    assert "typed-agents.md" in mkdocs
