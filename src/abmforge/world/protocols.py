from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SpaceProtocol(Protocol):
    """Minimum protocol for ABMForge spatial containers.

    A space implementation should support placing, moving, removing,
    locating, and querying agents.
    """

    def place(self, agent: Any, position: Any) -> None:
        """Place an agent at a position."""

    def move(self, agent: Any, position: Any) -> None:
        """Move a placed agent to a new position."""

    def remove(self, agent: Any) -> None:
        """Remove a placed agent from the space."""

    def position_of(self, agent: Any) -> Any:
        """Return the position of a placed agent."""

    def agents_at(self, position: Any) -> list[Any]:
        """Return agents at a position."""

    def neighbors(self, agent_or_position: Any, **kwargs: Any) -> list[Any]:
        """Return neighboring agents."""
