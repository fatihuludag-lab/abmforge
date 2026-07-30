from __future__ import annotations

from collections import defaultdict
from typing import Any

from abmforge.world._integrity import (
    clear_spatial_attributes,
    ensure_new_placement,
    resolve_placed_agent,
)

Position = tuple[int, int]


class GridWorld:
    """A simple two-dimensional grid world."""

    def __init__(
        self,
        width: int,
        height: int,
        *,
        torus: bool = False,
        multi: bool = True,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")

        self.width = width
        self.height = height
        self.torus = torus
        self.multi = multi
        self._cells: dict[
            Position,
            list[Any],
        ] = defaultdict(list)
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

        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"position out of bounds: {position!r}")

        return position

    def place(
        self,
        agent: Any,
        position: Position,
    ) -> None:
        """Place an agent at a position."""
        pos = self.normalize(position)

        ensure_new_placement(
            agent,
            space=self,
            positions=self._positions,
            agents=self._agents,
        )

        if not self.multi and self._cells.get(pos):
            raise ValueError(f"cell is occupied: {pos!r}")

        self._cells[pos].append(agent)
        self._positions[agent.unique_id] = pos
        self._agents[agent.unique_id] = agent

        agent.world = self
        agent.pos = pos

    def move(
        self,
        agent: Any,
        position: Position,
    ) -> None:
        """Move a placed agent to a new position."""
        _, stored, old = resolve_placed_agent(
            agent,
            positions=self._positions,
            agents=self._agents,
        )

        new = self.normalize(position)

        if not self.multi and self._cells.get(new) and old != new:
            raise ValueError(f"cell is occupied: {new!r}")

        self._cells[old].remove(stored)

        if not self._cells[old]:
            del self._cells[old]

        self._cells[new].append(stored)
        self._positions[stored.unique_id] = new
        stored.pos = new

    def remove(
        self,
        agent: Any,
    ) -> None:
        """Remove a placed agent from the grid."""
        unique_id, stored, position = resolve_placed_agent(
            agent,
            positions=self._positions,
            agents=self._agents,
        )

        self._cells[position].remove(stored)

        if not self._cells[position]:
            del self._cells[position]

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

    def agents_at(
        self,
        position: Position,
    ) -> list[Any]:
        """Return agents at a position."""
        return list(
            self._cells.get(
                self.normalize(position),
                [],
            )
        )

    def neighbors(
        self,
        agent_or_position: Any,
        *,
        radius: int = 1,
        include_center: bool = False,
    ) -> list[Any]:
        """Return neighboring agents within Chebyshev radius."""
        if radius < 0:
            raise ValueError("radius must be non-negative")

        if isinstance(
            agent_or_position,
            tuple,
        ):
            center = self.normalize(agent_or_position)
            source_id = None
        else:
            center = self.position_of(agent_or_position)
            source_id = agent_or_position.unique_id

        found: list[Any] = []
        cx, cy = center
        seen_positions: set[Position] = set()

        for dx in range(
            -radius,
            radius + 1,
        ):
            for dy in range(
                -radius,
                radius + 1,
            ):
                if dx == 0 and dy == 0 and not include_center:
                    continue

                try:
                    pos = self.normalize(
                        (
                            cx + dx,
                            cy + dy,
                        )
                    )
                except ValueError:
                    continue

                if pos in seen_positions:
                    continue

                seen_positions.add(pos)

                for agent in self._cells.get(
                    pos,
                    [],
                ):
                    if (
                        source_id is not None
                        and agent.unique_id == source_id
                        and not include_center
                    ):
                        continue

                    found.append(agent)

        return found

    def is_empty(
        self,
        position: Position,
    ) -> bool:
        """Return whether a cell has no agents."""
        return not self.agents_at(position)
