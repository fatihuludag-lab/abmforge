from __future__ import annotations

import math
from typing import Any

from abmforge.world._integrity import (
    clear_spatial_attributes,
    ensure_new_placement,
    resolve_placed_agent,
)

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
        self._positions: dict[
            int | str,
            Position,
        ] = {}
        self._agents: dict[
            int | str,
            Any,
        ] = {}

    def normalize(
        self,
        position: Position,
    ) -> Position:
        """Normalize a position according to torus/bounds rules."""
        x, y = position

        if self.torus:
            return (
                x % self.width,
                y % self.height,
            )

        if not (0 <= x <= self.width and 0 <= y <= self.height):
            raise ValueError(f"position out of bounds: {position!r}")

        return position

    def place(
        self,
        agent: Any,
        position: Position,
    ) -> None:
        """Place an agent at a continuous position."""
        pos = self.normalize(position)

        ensure_new_placement(
            agent,
            space=self,
            positions=self._positions,
            agents=self._agents,
        )

        self._agents[agent.unique_id] = agent
        self._positions[agent.unique_id] = pos
        agent.world = self
        agent.pos = pos

    def move(
        self,
        agent: Any,
        position: Position,
    ) -> None:
        """Move an agent to a new continuous position."""
        unique_id, stored, _ = resolve_placed_agent(
            agent,
            positions=self._positions,
            agents=self._agents,
        )

        pos = self.normalize(position)
        self._positions[unique_id] = pos
        stored.pos = pos

    def remove(
        self,
        agent: Any,
    ) -> None:
        """Remove an agent from the space."""
        unique_id, stored, _ = resolve_placed_agent(
            agent,
            positions=self._positions,
            agents=self._agents,
        )

        del self._positions[unique_id]
        del self._agents[unique_id]

        clear_spatial_attributes(
            stored,
            space=self,
        )

    def position_of(
        self,
        agent: Any,
    ) -> Position:
        """Return an agent's position."""
        _, _, position = resolve_placed_agent(
            agent,
            positions=self._positions,
            agents=self._agents,
        )

        return position

    def distance(
        self,
        a: Any,
        b: Any,
    ) -> float:
        """Return Euclidean distance between two agents or positions."""
        ax, ay = self.position_of(a) if not isinstance(a, tuple) else a
        bx, by = self.position_of(b) if not isinstance(b, tuple) else b

        dx = abs(ax - bx)
        dy = abs(ay - by)

        if self.torus:
            dx = min(
                dx,
                self.width - dx,
            )
            dy = min(
                dy,
                self.height - dy,
            )

        return math.sqrt(dx * dx + dy * dy)

    def agents_at(
        self,
        position: Position,
    ) -> list[Any]:
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
                and not isinstance(
                    agent_or_position,
                    tuple,
                )
                and agent.unique_id == agent_or_position.unique_id
            ):
                continue

            if (
                self.distance(
                    agent_or_position,
                    agent,
                )
                <= radius
            ):
                found.append(agent)

        return found
