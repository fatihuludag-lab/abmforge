from __future__ import annotations

from collections import defaultdict
from typing import Any

Position = tuple[int, int]


class GridWorld:
    """A simple two-dimensional grid world."""

    def __init__(self, width: int, height: int, *, torus: bool = False, multi: bool = True) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        self.width = width
        self.height = height
        self.torus = torus
        self.multi = multi
        self._cells: dict[Position, list[Any]] = defaultdict(list)
        self._positions: dict[int | str, Position] = {}

    def normalize(self, position: Position) -> Position:
        """Normalize a position according to torus/bounds rules."""
        x, y = position
        if self.torus:
            return (x % self.width, y % self.height)
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"position out of bounds: {position!r}")
        return (x, y)

    def place(self, agent: Any, position: Position) -> None:
        """Place an agent at a position."""
        pos = self.normalize(position)
        if agent.unique_id in self._positions:
            raise ValueError(f"agent is already placed: {agent.unique_id!r}")
        if not self.multi and self._cells[pos]:
            raise ValueError(f"cell is occupied: {pos!r}")
        self._cells[pos].append(agent)
        self._positions[agent.unique_id] = pos
        agent.world = self
        agent.pos = pos

    def move(self, agent: Any, position: Position) -> None:
        """Move a placed agent to a new position."""
        old = self.position_of(agent)
        new = self.normalize(position)
        if not self.multi and self._cells[new] and old != new:
            raise ValueError(f"cell is occupied: {new!r}")
        self._cells[old].remove(agent)
        if not self._cells[old]:
            del self._cells[old]
        self._cells[new].append(agent)
        self._positions[agent.unique_id] = new
        agent.pos = new

    def remove(self, agent: Any) -> None:
        """Remove an agent from the grid."""
        pos = self.position_of(agent)
        self._cells[pos].remove(agent)
        if not self._cells[pos]:
            del self._cells[pos]
        del self._positions[agent.unique_id]
        if hasattr(agent, "pos"):
            delattr(agent, "pos")

    def position_of(self, agent: Any) -> Position:
        """Return an agent's position."""
        unique_id = getattr(agent, "unique_id", agent)
        try:
            return self._positions[unique_id]
        except KeyError as exc:
            raise KeyError(f"agent is not placed: {unique_id!r}") from exc

    def agents_at(self, position: Position) -> list[Any]:
        """Return agents at a position."""
        return list(self._cells.get(self.normalize(position), []))

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

        if isinstance(agent_or_position, tuple):
            center = self.normalize(agent_or_position)
            source_id = None
        else:
            center = self.position_of(agent_or_position)
            source_id = agent_or_position.unique_id

        found: list[Any] = []
        cx, cy = center
        seen_positions: set[Position] = set()
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0 and not include_center:
                    continue
                try:
                    pos = self.normalize((cx + dx, cy + dy))
                except ValueError:
                    continue
                if pos in seen_positions:
                    continue
                seen_positions.add(pos)
                for agent in self._cells.get(pos, []):
                    if (
                        source_id is not None
                        and agent.unique_id == source_id
                        and not include_center
                    ):
                        continue
                    found.append(agent)
        return found

    def is_empty(self, position: Position) -> bool:
        """Return whether a cell has no agents."""
        return not self.agents_at(position)
