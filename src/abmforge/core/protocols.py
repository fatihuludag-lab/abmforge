from __future__ import annotations

from typing import Any, Protocol, TypeVar, runtime_checkable

AgentID = int | str
StateT = TypeVar("StateT")


@runtime_checkable
class AgentLike(Protocol):
    """Structural protocol for ABMForge-like agents.

    This protocol is intentionally minimal. It describes the attributes that
    schedulers, collections, and user utilities commonly need without requiring
    users to inherit from a new typed-agent base class.
    """

    model: Any
    unique_id: AgentID
    is_alive: bool


@runtime_checkable
class SteppableAgent(AgentLike, Protocol):
    """Protocol for agents that can be activated with ``step()``."""

    def step(self) -> None:
        """Advance the agent by one activation."""


@runtime_checkable
class AdvanceableAgent(Protocol):
    """Protocol for agents that support a second-phase ``advance()`` step."""

    def advance(self) -> None:
        """Commit state updates after an initial step phase."""


@runtime_checkable
class StatefulAgent(AgentLike, Protocol[StateT]):
    """Protocol for agents that expose a typed ``state`` attribute."""

    state: StateT


__all__ = [
    "AdvanceableAgent",
    "AgentID",
    "AgentLike",
    "StateT",
    "StatefulAgent",
    "SteppableAgent",
]
