from __future__ import annotations

import math
from typing import Any

Position = tuple[float, float]


class ContinuousSpace:
    """A simple two-dimensional continuous space."""

    def __init__(
        self,
        width: float,
        height: float,
        *,
        torus: bool = False,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")

        self.width = width
        self.height = height
        self.torus = torus
        self._positions: dict[int | str, Position] = {}
        self._agents: dict[int | str, Any] = {}

    def normalize(self, position: Position) -> Position:
        """Normalize a position according to torus/bounds rules."""
        x, y = position

        if self.torus:
            return (x % self.width, y % self.height)

        if not (0 <= x <= self.width and 0 <= y <= self.height):
            raise ValueError(f"position out of bounds: {position!r}")

        return (x, y)

    def place(self, agent: Any, position: Position) -> None:
        """Place an agent at a continuous position."""
        pos = self.normalize(position)

        if agent.unique_id in self._positions:
            raise ValueError(f"agent is already placed: {agent.unique_id!r}")

        self._agents[agent.unique_id] = agent
        self._positions[agent.unique_id] = pos
        agent.world = self
        agent.pos = pos

    def move(self, agent: Any, position: Position) -> None:
        """Move an agent to a new continuous position."""
        if agent.unique_id not in self._positions:
            raise KeyError(f"agent is not placed: {agent.unique_id!r}")

        pos = self.normalize(position)
        self._positions[agent.unique_id] = pos
        agent.pos = pos

    def remove(self, agent: Any) -> None:
        """Remove an agent from the space."""
        if agent.unique_id not in self._positions:
            raise KeyError(f"agent is not placed: {agent.unique_id!r}")

        del self._positions[agent.unique_id]
        self._agents.pop(agent.unique_id, None)

        if hasattr(agent, "pos"):
            delattr(agent, "pos")

    def position_of(self, agent: Any) -> Position:
        """Return an agent's position."""
        unique_id = getattr(agent, "unique_id", agent)

        try:
            return self._positions[unique_id]
        except KeyError as exc:
            raise KeyError(f"agent is not placed: {unique_id!r}") from exc

    def distance(self, a: Any, b: Any) -> float:
        """Return Euclidean distance between two agents or positions."""
        ax, ay = self.position_of(a) if not isinstance(a, tuple) else a
        bx, by = self.position_of(b) if not isinstance(b, tuple) else b

        dx = abs(ax - bx)
        dy = abs(ay - by)

        if self.torus:
            dx = min(dx, self.width - dx)
            dy = min(dy, self.height - dy)

        return math.sqrt(dx * dx + dy * dy)

    def agents_at(self, position: tuple[float, float]) -> list[Any]:
        """Return agents exactly at a continuous-space position."""
        normalized = self.normalize(position)

        return [
            self._agents[agent_id]
            for agent_id, agent_position in self._positions.items()
            if agent_position == normalized
        ]

    def neighbors(
        self,
        agent_or_position: Any,
        *,
        radius: float,
        include_center: bool = False,
    ) -> list[Any]:
        """Return agents within a Euclidean radius."""
        found = []

        for agent in self._agents.values():
            if (
                not include_center
                and not isinstance(agent_or_position, tuple)
                and agent.unique_id == agent_or_position.unique_id
            ):
                continue

            if self.distance(agent_or_position, agent) <= radius:
                found.append(agent)

        return found
